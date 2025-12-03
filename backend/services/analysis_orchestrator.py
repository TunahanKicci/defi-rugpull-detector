"""
Analysis Orchestrator - Coordinates all analysis modules
"""
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from modules import (
    a_contract_security,
    b_holder_analysis,
    c_liquidity_pool,
    d_transfer_anomaly,
    e_pattern_matching,
    f_tokenomics,
    h_ml_risk_scorer
)
# Honeypot simulator is separate - not part of main modules
from modules import i_honeypot_simulator
from services.blockchain.ethereum import EthereumChain
from services.blockchain.bsc import BSCChain
from services.blockchain.polygon import PolygonChain
from services.cache_manager import CacheManager
from utils.formatters import format_risk_level
from api.models.response import AnalysisResponse, ModuleResult, ContractInfo

logger = logging.getLogger(__name__)


class AnalysisOrchestrator:
    """
    Coordinates all analysis modules and aggregates results
    """
    
    def __init__(self, chain: str = "ethereum"):
        self.chain_name = chain.lower()
        self.blockchain = self._get_blockchain_client()
        self.cache = CacheManager()
        
        # Initialize modules
        self.modules = {
            "contract_security": a_contract_security,
            "holder_analysis": b_holder_analysis,
            "liquidity_pool": c_liquidity_pool,
            "transfer_anomaly": d_transfer_anomaly,
            "pattern_matching": e_pattern_matching,
            "tokenomics": f_tokenomics,
        }
        
        # Honeypot simulator - separate from main modules
        self.honeypot_simulator = i_honeypot_simulator
        
        self.ml_scorer = h_ml_risk_scorer
    
    def _get_blockchain_client(self):
        """Get appropriate blockchain client"""
        if self.chain_name == "ethereum":
            return EthereumChain()
        elif self.chain_name == "bsc":
            return BSCChain()
        elif self.chain_name == "polygon":
            return PolygonChain()
        else:
            raise ValueError(f"Unsupported chain: {self.chain_name}")
    
    async def analyze(self, address: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Run complete analysis on a token
        
        Args:
            address: Token contract address
            force_refresh: Force refresh cached data (ignored - cache disabled)
            
        Returns:
            Complete analysis result
        """
        start_time = time.time()
        logger.info(f"Starting analysis for {address} on {self.chain_name}")
        
        # Cache disabled - always run fresh analysis
        
        try:
            # Step 1: Get basic contract info
            contract_info = await self._get_contract_info(address)
            
            # Step 2: Run all analysis modules
            module_results = await self._run_modules(address)
            
            # Step 2.5: Run honeypot simulation (SEPARATE - not part of module results)
            honeypot_result = None
            try:
                logger.info(f"Running honeypot simulation for {address}...")
                # Pass liquidity USD from liquidity module if available
                liquidity_usd = None
                try:
                    lp = module_results.get("liquidity_pool", {})
                    liquidity_usd = lp.get("data", {}).get("liquidity_usd")
                except Exception:
                    liquidity_usd = None
                honeypot_result = await self.honeypot_simulator.analyze(address, self.blockchain, liquidity_usd=liquidity_usd)
            except Exception as e:
                logger.warning(f"Honeypot simulation failed: {e}")
                honeypot_result = {
                    "error": str(e),
                    "verdict": "UNKNOWN",
                    "data": {},
                    "warnings": []
                }
            
            # Step 3: Extract features for ML
            features = self._extract_features(module_results)
            
            # Step 4: Calculate ML risk score
            ml_result = await self.ml_scorer.predict(features, module_results)
            
            # Step 5: Aggregate results
            result = self._aggregate_results(
                address=address,
                contract_info=contract_info,
                module_results=module_results,
                ml_result=ml_result,
                honeypot_result=honeypot_result  # Pass honeypot result separately
            )
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            result["analysis_duration_ms"] = round(duration_ms, 2)
            result["cached"] = False
            
            # Cache disabled - no caching
            
            logger.info(f"Analysis completed for {address} in {duration_ms:.2f}ms - Risk: {result['risk_score']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed for {address}: {str(e)}", exc_info=True)
            # Don't cache failures
            raise
    
    async def quick_check(self, address: str) -> Dict[str, Any]:
        """
        Quick check using cached data only
        
        Args:
            address: Token contract address
            
        Returns:
            Quick check result
        """
        # Check if in known scam database
        is_scam = await e_pattern_matching.is_known_scam(address)
        
        if is_scam:
            return {
                "address": address,
                "chain": self.chain_name,
                "risk_score": 100,
                "risk_level": "CRITICAL",
                "is_known_scam": True,
                "cached": True
            }
        
        # Try to get cached full analysis
        cached = await self.cache.get_analysis(address, self.chain_name)
        if cached:
            return {
                "address": address,
                "chain": self.chain_name,
                "risk_score": cached.get("risk_score", 50),
                "risk_level": cached.get("risk_level", "MEDIUM"),
                "is_known_scam": False,
                "cached": True
            }
        
        # No data available
        return {
            "address": address,
            "chain": self.chain_name,
            "risk_score": 50,
            "risk_level": "UNKNOWN",
            "is_known_scam": False,
            "cached": False,
            "message": "No cached data available. Run full analysis."
        }
    
    async def _get_contract_info(self, address: str) -> ContractInfo:
        """Get basic contract information"""
        try:
            info = await self.blockchain.get_contract_info(address)
            return ContractInfo(
                address=address,
                name=info.get("name"),
                symbol=info.get("symbol"),
                decimals=info.get("decimals"),
                total_supply=info.get("total_supply"),
                chain=self.chain_name
            )
        except Exception as e:
            logger.warning(f"Failed to get contract info: {str(e)}")
            return ContractInfo(address=address, chain=self.chain_name)
    
    async def _run_modules(self, address: str) -> Dict[str, Dict[str, Any]]:
        """Run all analysis modules"""
        results = {}
        
        for module_name, module in self.modules.items():
            try:
                logger.debug(f"Running module: {module_name}")
                result = await module.analyze(address, self.blockchain)
                
                # CRITICAL LOGIC: A module = 0 risk is SUSPICIOUS for unknown tokens
                # Legitimate tokens ALWAYS have risk factors (ownership, functions, etc.)
                # 0 risk = bytecode unavailable/obfuscated = SCAM INDICATOR
                if module_name == "contract_security" and result.get("risk_score", 0) == 0:
                    warnings = result.get("warnings", [])
                    if not warnings or len(warnings) == 0:
                        logger.warning(f"⚠️ A module: 0 risk with no warnings = SUSPICIOUS bytecode")
                        result["risk_score"] = 50
                        result["warnings"] = [
                            "🚨 CRITICAL: Contract bytecode unavailable or obfuscated",
                            "⚠️ Cannot verify contract safety - HIGH RISK"
                        ]
                
                results[module_name] = result
            except Exception as e:
                logger.error(f"Module {module_name} failed: {str(e)}")
                results[module_name] = {
                    "error": str(e),
                    "risk_score": 50,
                    "warnings": [f"Module failed: {str(e)}"]
                }
        
        return results
    
    def _extract_features(self, module_results: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """Extract numerical features for ML model"""
        features = {}
        
        # Extract features from each module
        for module_name, result in module_results.items():
            if "features" in result:
                features.update(result["features"])
        
        return features
    
    def _aggregate_results(
        self,
        address: str,
        contract_info: ContractInfo,
        module_results: Dict[str, Dict[str, Any]],
        ml_result: Dict[str, Any],
        honeypot_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Aggregate all results into final response"""
        
        # Convert module results to ModuleResult objects
        modules = {}
        all_warnings = []
        red_flags = []
        
        for module_name, result in module_results.items():
            warnings = result.get("warnings", [])
            all_warnings.extend(warnings)
            
            # Identify red flags (high severity warnings)
            if result.get("risk_score", 0) >= 70:
                red_flags.extend(warnings[:2])  # Take top 2 warnings as red flags
            
            modules[module_name] = ModuleResult(
                module_name=module_name,
                risk_score=result.get("risk_score", 50),
                warnings=warnings,
                data=result.get("data", {})
            )
        
        # Get final risk score from ML
        risk_score = ml_result.get("risk_score", 50)
        risk_level = format_risk_level(risk_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_score, red_flags)
        
        return {
            "address": address,
            "chain": self.chain_name,
            "contract_info": contract_info.model_dump(),
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "modules": {k: v.model_dump() for k, v in modules.items()},
            "honeypot_simulation": honeypot_result,  # SEPARATE FIELD - not in modules
            "warnings": all_warnings,
            "red_flags": list(set(red_flags))[:5],  # Top 5 unique red flags
            "recommendations": recommendations,
            "feature_importance": ml_result.get("feature_importance"),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _generate_recommendations(self, risk_score: float, red_flags: List[str]) -> List[str]:
        """Generate user-friendly recommendations"""
        recommendations = []
        
        if risk_score >= 80:
            recommendations.append("⛔ AVOID: This token shows critical risk factors")
            recommendations.append("🚨 Do NOT invest - high probability of rug pull")
        elif risk_score >= 60:
            recommendations.append("⚠️ HIGH RISK: Exercise extreme caution")
            recommendations.append("💡 Only invest what you can afford to lose")
        elif risk_score >= 40:
            recommendations.append("⚡ MEDIUM RISK: Conduct thorough due diligence")
            recommendations.append("📊 Monitor liquidity and holder distribution")
        else:
            recommendations.append("✅ Lower risk detected, but always DYOR")
            recommendations.append("🔍 Continue monitoring for changes")
        
        if len(red_flags) > 0:
            recommendations.append(f"🔴 {len(red_flags)} critical issue(s) detected")
        
        return recommendations
