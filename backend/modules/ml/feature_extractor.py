"""
Feature Extractor
Extracts and engineers features from module results for ML models
"""
import logging
from typing import Dict, Any, List
import numpy as np

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extract and engineer features for ML models"""
    
    def __init__(self):
        self.feature_names = []
        
    def extract(self, module_results: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """
        Extract comprehensive features from module results
        
        Args:
            module_results: Results from all analysis modules
            
        Returns:
            Feature dictionary
        """
        features = {}
        
        # Contract Security Features
        contract = module_results.get("contract_security", {})
        features["has_bytecode"] = 1.0 if contract.get("has_bytecode", False) else 0.0
        features["is_verified"] = 1.0 if contract.get("is_verified", False) else 0.0
        features["has_selfdestruct"] = 1.0 if contract.get("has_selfdestruct", False) else 0.0
        features["has_delegatecall"] = 1.0 if contract.get("has_delegatecall", False) else 0.0
        features["is_proxy"] = 1.0 if contract.get("is_proxy", False) else 0.0
        features["has_owner"] = 1.0 if contract.get("has_owner", False) else 0.0
        features["is_pausable"] = 1.0 if contract.get("is_pausable", False) else 0.0
        features["contract_risk_score"] = contract.get("risk_score", 50.0) / 100.0
        
        # Holder Analysis Features
        holder = module_results.get("holder_analysis", {})
        features["top_10_concentration"] = holder.get("top_10_concentration", 0.5)
        features["top_holder_pct"] = holder.get("top_holder_percentage", 0.0) / 100.0
        features["gini_coefficient"] = holder.get("gini_coefficient", 0.5)
        features["unique_holders"] = min(holder.get("unique_holders", 0) / 10000.0, 1.0)
        features["holder_risk_score"] = holder.get("risk_score", 50.0) / 100.0
        
        # Liquidity Pool Features
        liquidity = module_results.get("liquidity_pool", {})
        features["lp_locked"] = 1.0 if liquidity.get("is_locked", False) else 0.0
        features["liquidity_usd"] = min(liquidity.get("liquidity_usd", 0) / 1000000.0, 1.0)
        features["has_pair"] = 1.0 if liquidity.get("has_pair", False) else 0.0
        features["liquidity_risk_score"] = liquidity.get("risk_score", 50.0) / 100.0
        
        # Transfer Anomaly Features
        transfer = module_results.get("transfer_anomaly", {})
        features["mint_count"] = min(transfer.get("mint_count", 0) / 10.0, 1.0)
        features["burn_count"] = min(transfer.get("burn_count", 0) / 10.0, 1.0)
        features["unique_senders"] = min(transfer.get("unique_senders", 0) / 1000.0, 1.0)
        features["unique_receivers"] = min(transfer.get("unique_receivers", 0) / 1000.0, 1.0)
        features["avg_transfer_value"] = min(transfer.get("avg_transfer_value", 0) / 1000000.0, 1.0)
        features["anomaly_score"] = transfer.get("anomaly_score", 0.5)
        features["transfer_risk_score"] = transfer.get("risk_score", 50.0) / 100.0
        
        # Pattern Matching Features
        pattern = module_results.get("pattern_matching", {})
        features["is_known_scam"] = 1.0 if pattern.get("is_known_scam", False) else 0.0
        features["honeypot_pattern"] = 1.0 if pattern.get("has_honeypot_pattern", False) else 0.0
        features["similarity_score"] = pattern.get("similarity_score", 0.0)
        features["pattern_risk_score"] = pattern.get("risk_score", 50.0) / 100.0
        
        # Tokenomics Features
        tokenomics = module_results.get("tokenomics", {})
        features["total_supply"] = min(tokenomics.get("total_supply", 0) / 1e15, 1.0)
        features["has_tax"] = 1.0 if tokenomics.get("has_tax", False) else 0.0
        features["buy_tax"] = tokenomics.get("buy_tax", 0.0) / 100.0
        features["sell_tax"] = tokenomics.get("sell_tax", 0.0) / 100.0
        features["total_tax"] = (features["buy_tax"] + features["sell_tax"]) / 2.0
        features["tokenomics_risk_score"] = tokenomics.get("risk_score", 50.0) / 100.0
        
        # Derived Features (Feature Engineering)
        features["risk_concentration"] = (
            features["top_10_concentration"] * features["gini_coefficient"]
        )
        features["liquidity_security"] = (
            features["lp_locked"] * features["liquidity_usd"]
        )
        features["contract_danger"] = (
            features["has_selfdestruct"] + 
            features["has_delegatecall"] + 
            features["is_proxy"]
        ) / 3.0
        features["activity_level"] = (
            features["unique_senders"] + features["unique_receivers"]
        ) / 2.0
        features["manipulation_risk"] = (
            features["mint_count"] + 
            features["anomaly_score"] + 
            features["honeypot_pattern"]
        ) / 3.0
        
        # Overall module risk (weighted average)
        module_risks = [
            features["contract_risk_score"] * 3.0,
            features["holder_risk_score"] * 2.0,
            features["liquidity_risk_score"] * 2.5,
            features["transfer_risk_score"] * 1.5,
            features["pattern_risk_score"] * 1.0,
            features["tokenomics_risk_score"] * 1.0
        ]
        features["module_risk_avg"] = sum(module_risks) / 11.0
        
        self.feature_names = list(features.keys())
        logger.info(f"Extracted {len(features)} features")
        
        return features
    
    def get_feature_vector(self, features: Dict[str, float]) -> np.ndarray:
        """Convert feature dict to numpy array"""
        return np.array([features.get(name, 0.0) for name in self.feature_names])
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names"""
        return self.feature_names
