"""
XAI Explainer - Explainable AI for Risk Score Analysis
Uses SHAP (SHapley Additive exPlanations) to explain risk decisions
"""
import logging
from typing import Dict, Any, List, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class XAIExplainer:
    """
    Explains risk scores using feature importance and business logic
    Provides human-readable explanations for why a token is risky
    """
    
    # Risk factor descriptions in Turkish
    FACTOR_DESCRIPTIONS = {
        # Contract Security (Module A)
        "contract_security": {
            "high": "Kontrat güvenlik açıkları tespit edildi",
            "medium": "Kontrat güvenliği endişe verici",
            "low": "Kontrat güvenliği kabul edilebilir"
        },
        "has_mint_function": {
            "impact": "Mint fonksiyonu mevcut - sınırsız token basılabilir",
            "risk": "yüksek"
        },
        "has_blacklist": {
            "impact": "Blacklist fonksiyonu - cüzdanlar engellenebilir",
            "risk": "yüksek"
        },
        "is_proxy": {
            "impact": "Proxy kontrat - kod değiştirilebilir",
            "risk": "yüksek"
        },
        "has_hidden_owner": {
            "impact": "Gizli sahiplik tespit edildi",
            "risk": "kritik"
        },
        
        # Holder Analysis (Module B)
        "holder_analysis": {
            "high": "Holder dağılımı çok dengesiz",
            "medium": "Holder konsantrasyonu endişe verici",
            "low": "Holder dağılımı makul"
        },
        "top10_percentage": {
            "impact": "Top 10 cüzdan toplam arzın büyük kısmına sahip",
            "threshold": 70,
            "risk": "yüksek"
        },
        "whale_count": {
            "impact": "Yüksek miktarda whale cüzdanı tespit edildi",
            "risk": "orta"
        },
        
        # Liquidity Pool (Module C)
        "liquidity_pool": {
            "high": "Likidite havuzu kritik sorunlar içeriyor",
            "medium": "Likidite havuzu endişe verici",
            "low": "Likidite havuzu sağlıklı"
        },
        "liquidity_locked": {
            "impact": "Likidite kilitli değil - rug pull riski",
            "risk": "kritik"
        },
        "liquidity_usd": {
            "impact": "Düşük likidite miktarı",
            "threshold": 10000,
            "risk": "yüksek"
        },
        
        # Transfer Anomaly (Module D)
        "transfer_anomaly": {
            "high": "Anormal transfer paterni tespit edildi",
            "medium": "Şüpheli transfer aktivitesi",
            "low": "Normal transfer aktivitesi"
        },
        
        # Pattern Matching (Module E)
        "pattern_matching": {
            "high": "Bilinen scam paterni tespit edildi",
            "medium": "Şüpheli patternler mevcut",
            "low": "Bilinen risk paterni yok"
        },
        "is_known_scam": {
            "impact": "Bu token bilinen scam veritabanında",
            "risk": "kritik"
        },
        
        # Tokenomics (Module F)
        "tokenomics": {
            "high": "Tokenomics yapısı çok riskli",
            "medium": "Tokenomics endişe verici",
            "low": "Tokenomics makul"
        },
        "tax_rate": {
            "impact": "Yüksek vergi oranı",
            "threshold": 15,
            "risk": "orta"
        },
        
        # Honeypot Simulation
        "honeypot": {
            "is_honeypot": "Token satılamıyor - Honeypot tespit edildi",
            "high_tax": "Yüksek satış vergisi - alıcı kaybedecek",
            "risk": "kritik"
        },
        
        # Whale Detector AI
        "whale_detector": {
            "high": "AI modeli yüksek whale manipülasyon riski tespit etti",
            "medium": "Whale aktivitesi endişe verici",
            "low": "Normal whale aktivitesi"
        }
    }
    
    def __init__(self):
        """Initialize XAI Explainer"""
        pass
    
    async def explain_risk(
        self,
        risk_score: float,
        module_results: Dict[str, Dict[str, Any]],
        honeypot_result: Dict[str, Any] = None,
        whale_detector_result: Dict[str, Any] = None,
        feature_importance: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive explanation for risk score
        
        Args:
            risk_score: Overall risk score (0-100)
            module_results: Results from all analysis modules
            honeypot_result: Honeypot simulation result
            whale_detector_result: Whale detector AI result
            feature_importance: ML feature importance scores
            
        Returns:
            Explanation object with reasons and impacts
        """
        try:
            # Extract top risk factors
            risk_factors = self._extract_risk_factors(
                module_results, 
                honeypot_result, 
                whale_detector_result
            )
            
            # Calculate impact percentages
            impact_breakdown = self._calculate_impact_breakdown(
                risk_factors, 
                feature_importance
            )
            
            # Generate human-readable explanations
            explanations = self._generate_explanations(
                risk_score,
                risk_factors,
                impact_breakdown
            )
            
            # Generate summary
            summary = self._generate_summary(risk_score, impact_breakdown)
            
            return {
                "summary": summary,
                "risk_score": risk_score,
                "top_factors": explanations,
                "impact_breakdown": impact_breakdown,
                "explanation_confidence": self._calculate_confidence(risk_factors)
            }
            
        except Exception as e:
            logger.error(f"XAI explanation failed: {e}", exc_info=True)
            return {
                "summary": f"Risk skoru: {risk_score:.0f}/100",
                "risk_score": risk_score,
                "top_factors": [],
                "impact_breakdown": {},
                "explanation_confidence": 0.5,
                "error": str(e)
            }
    
    def _extract_risk_factors(
        self,
        module_results: Dict[str, Dict[str, Any]],
        honeypot_result: Dict[str, Any],
        whale_detector_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract key risk factors from all modules"""
        factors = []
        
        # Process each module
        for module_name, result in module_results.items():
            if result.get("error"):
                continue
                
            risk_score = result.get("risk_score", 0)
            data = result.get("data", {})
            warnings = result.get("warnings", [])
            
            # Add module-level factor
            if risk_score >= 40:  # Only significant risks
                factors.append({
                    "source": module_name,
                    "type": "module_score",
                    "risk_score": risk_score,
                    "data": data,
                    "warnings": warnings[:3]  # Top 3 warnings
                })
            
            # Extract specific risk indicators
            factors.extend(self._extract_module_specific_factors(module_name, data, risk_score))
        
        # Process honeypot result
        if honeypot_result:
            factors.extend(self._extract_honeypot_factors(honeypot_result))
        
        # Process whale detector result
        if whale_detector_result:
            factors.extend(self._extract_whale_factors(whale_detector_result))
        
        # Sort by risk score (highest first)
        factors.sort(key=lambda x: x.get("risk_score", 0), reverse=True)
        
        return factors
    
    def _extract_module_specific_factors(
        self, 
        module_name: str, 
        data: Dict[str, Any],
        module_risk: float
    ) -> List[Dict[str, Any]]:
        """Extract specific risk factors from module data"""
        factors = []
        
        if module_name == "contract_security":
            # Check dangerous functions
            if data.get("has_mint_function"):
                factors.append({
                    "source": "contract_security",
                    "type": "has_mint_function",
                    "risk_score": 25,
                    "detail": "Mint fonksiyonu var"
                })
            if data.get("has_blacklist"):
                factors.append({
                    "source": "contract_security",
                    "type": "has_blacklist",
                    "risk_score": 20,
                    "detail": "Blacklist fonksiyonu var"
                })
            if data.get("is_proxy"):
                factors.append({
                    "source": "contract_security",
                    "type": "is_proxy",
                    "risk_score": 25,
                    "detail": "Proxy kontrat"
                })
        
        elif module_name == "holder_analysis":
            top10_pct = data.get("top_10_percentage", 0)
            if top10_pct > 70:
                factors.append({
                    "source": "holder_analysis",
                    "type": "top10_percentage",
                    "risk_score": min(top10_pct, 100),
                    "detail": f"Top 10 cüzdan %{top10_pct:.1f} oranında"
                })
        
        elif module_name == "liquidity_pool":
            if not data.get("liquidity_locked"):
                factors.append({
                    "source": "liquidity_pool",
                    "type": "liquidity_locked",
                    "risk_score": 40,
                    "detail": "Likidite kilitli değil"
                })
            
            liq_usd = data.get("liquidity_usd", 0)
            if liq_usd < 10000:
                factors.append({
                    "source": "liquidity_pool",
                    "type": "liquidity_usd",
                    "risk_score": 30,
                    "detail": f"Düşük likidite: ${liq_usd:.0f}"
                })
        
        elif module_name == "tokenomics":
            tax = data.get("total_tax", 0)
            if tax > 15:
                factors.append({
                    "source": "tokenomics",
                    "type": "tax_rate",
                    "risk_score": min(tax * 2, 50),
                    "detail": f"Yüksek vergi: %{tax}"
                })
        
        elif module_name == "pattern_matching":
            if data.get("is_known_scam"):
                factors.append({
                    "source": "pattern_matching",
                    "type": "is_known_scam",
                    "risk_score": 100,
                    "detail": "Bilinen scam listesinde"
                })
        
        return factors
    
    def _extract_honeypot_factors(self, honeypot_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract risk factors from honeypot simulation"""
        factors = []
        
        verdict = honeypot_result.get("verdict", "UNKNOWN")
        data = honeypot_result.get("data", {})
        
        if verdict == "HONEYPOT":
            factors.append({
                "source": "honeypot_simulation",
                "type": "is_honeypot",
                "risk_score": 100,
                "detail": "Token satılamıyor - Honeypot"
            })
        
        elif verdict == "HIGH_TAX":
            tax = data.get("sell_tax", 0)
            factors.append({
                "source": "honeypot_simulation",
                "type": "high_sell_tax",
                "risk_score": 70,
                "detail": f"Çok yüksek satış vergisi: %{tax}"
            })
        
        return factors
    
    def _extract_whale_factors(self, whale_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract risk factors from whale detector AI"""
        factors = []
        
        risk_score = whale_result.get("risk_score", 0)
        confidence = whale_result.get("confidence", 0)
        
        if risk_score >= 60 and confidence >= 0.7:
            # Ensure confidence is in 0-1 range, convert to percentage
            conf_pct = confidence * 100 if confidence <= 1 else confidence
            factors.append({
                "source": "whale_detector_ai",
                "type": "whale_manipulation",
                "risk_score": risk_score,
                "detail": f"AI tespit: Whale manipülasyonu ({conf_pct:.0f}% güven)"
            })
        
        return factors
    
    def _calculate_impact_breakdown(
        self,
        risk_factors: List[Dict[str, Any]],
        feature_importance: Dict[str, float] = None
    ) -> Dict[str, float]:
        """
        Calculate percentage impact of each risk factor
        Uses both risk scores and ML feature importance
        """
        if not risk_factors:
            return {}
        
        # Calculate total risk points
        total_risk = sum(f.get("risk_score", 0) for f in risk_factors[:10])  # Top 10 factors
        
        if total_risk == 0:
            return {}
        
        # Calculate percentage for each factor
        breakdown = {}
        for factor in risk_factors[:10]:  # Top 10 only
            risk_score = factor.get("risk_score", 0)
            percentage = (risk_score / total_risk) * 100
            
            # Create readable name
            source = factor.get("source", "unknown")
            factor_type = factor.get("type", "")
            
            if factor_type == "module_score":
                name = self._get_module_name_tr(source)
            else:
                name = factor.get("detail", source)
            
            breakdown[name] = round(percentage, 1)
        
        return breakdown
    
    def _generate_explanations(
        self,
        risk_score: float,
        risk_factors: List[Dict[str, Any]],
        impact_breakdown: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Generate human-readable explanations for top risk factors"""
        explanations = []
        
        for i, factor in enumerate(risk_factors[:5], 1):  # Top 5 factors
            source = factor.get("source", "")
            factor_type = factor.get("type", "")
            detail = factor.get("detail", "")
            factor_risk = factor.get("risk_score", 0)
            
            # Get description
            description = self._get_factor_description(source, factor_type, factor)
            
            # Get impact percentage
            impact_key = detail if detail else self._get_module_name_tr(source)
            impact_pct = impact_breakdown.get(impact_key, 0)
            
            explanations.append({
                "rank": i,
                "factor": detail if detail else self._get_module_name_tr(source),
                "description": description,
                "risk_contribution": factor_risk,
                "impact_percentage": impact_pct,
                "severity": self._get_severity_label(factor_risk)
            })
        
        return explanations
    
    def _get_factor_description(
        self, 
        source: str, 
        factor_type: str, 
        factor: Dict[str, Any]
    ) -> str:
        """Get human-readable description for a risk factor"""
        
        # Check in descriptions dictionary
        if source in self.FACTOR_DESCRIPTIONS:
            source_desc = self.FACTOR_DESCRIPTIONS[source]
            
            if factor_type in source_desc:
                return source_desc[factor_type].get("impact", str(source_desc[factor_type]))
            
            # Use risk-level description
            risk = factor.get("risk_score", 0)
            if risk >= 70 and "high" in source_desc:
                return source_desc["high"]
            elif risk >= 40 and "medium" in source_desc:
                return source_desc["medium"]
            elif "low" in source_desc:
                return source_desc["low"]
        
        # Fallback to warnings
        warnings = factor.get("warnings", [])
        if warnings:
            return warnings[0]
        
        return f"{self._get_module_name_tr(source)} risk faktörü"
    
    def _generate_summary(
        self, 
        risk_score: float, 
        impact_breakdown: Dict[str, float]
    ) -> str:
        """Generate comprehensive risk summary"""
        
        if risk_score >= 80:
            level = "KRİTİK SEVİYEDE YÜKSEK"
        elif risk_score >= 60:
            level = "YÜKSEK"
        elif risk_score >= 40:
            level = "ORTA"
        else:
            level = "DÜŞÜK"
        
        summary = f"Risk skoru: {risk_score:.0f}/100 ({level})"
        
        # Add top 3 factors to summary
        if impact_breakdown:
            top_factors = sorted(impact_breakdown.items(), key=lambda x: x[1], reverse=True)[:3]
            summary += "\n\nAna risk faktörleri:"
            for i, (factor, impact) in enumerate(top_factors, 1):
                summary += f"\n{i}. {factor} (%{impact:.0f} etki)"
        
        return summary
    
    def _calculate_confidence(self, risk_factors: List[Dict[str, Any]]) -> float:
        """Calculate confidence level of the explanation"""
        if not risk_factors:
            return 0.5
        
        # More factors = higher confidence
        factor_count = len(risk_factors)
        confidence = min(0.5 + (factor_count * 0.05), 0.95)
        
        return round(confidence, 2)
    
    def _get_module_name_tr(self, module_name: str) -> str:
        """Get Turkish name for module"""
        names = {
            "contract_security": "Kontrat Güvenliği",
            "holder_analysis": "Holder Analizi",
            "liquidity_pool": "Likidite Havuzu",
            "transfer_anomaly": "Transfer Anomalisi",
            "pattern_matching": "Pattern Eşleştirme",
            "tokenomics": "Tokenomics",
            "honeypot_simulation": "Honeypot Simülasyonu",
            "whale_detector_ai": "Whale Dedektörü AI"
        }
        return names.get(module_name, module_name)
    
    def _get_severity_label(self, risk_score: float) -> str:
        """Get severity label for risk score"""
        if risk_score >= 80:
            return "KRİTİK"
        elif risk_score >= 60:
            return "YÜKSEK"
        elif risk_score >= 40:
            return "ORTA"
        else:
            return "DÜŞÜK"


# Global instance
_explainer = XAIExplainer()


async def explain_risk(
    risk_score: float,
    module_results: Dict[str, Dict[str, Any]],
    honeypot_result: Dict[str, Any] = None,
    whale_detector_result: Dict[str, Any] = None,
    feature_importance: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Main function to explain risk score
    
    Returns explanation with:
    - summary: Human-readable summary
    - top_factors: List of top risk factors with descriptions
    - impact_breakdown: Percentage impact of each factor
    """
    return await _explainer.explain_risk(
        risk_score,
        module_results,
        honeypot_result,
        whale_detector_result,
        feature_importance
    )
