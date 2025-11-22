"""
Module H: ML Risk Scorer
Combines all features and predicts final risk score
"""
import logging
from typing import Dict, Any, List
import numpy as np

logger = logging.getLogger(__name__)


# Mock ML model (in production, load trained XGBoost/Random Forest)
class MockMLModel:
    """Simplified ML model for demonstration"""
    
    def predict(self, features: Dict[str, float]) -> float:
        """
        Predict risk score from features
        
        Args:
            features: Feature dictionary
            
        Returns:
            Risk score (0-100)
        """
        # Weighted sum of key features
        weights = {
            "is_known_scam": 100,
            "has_mint": 15,
            "has_selfdestruct": 20,
            "is_upgradeable": 15,
            "lp_locked": -20,  # Negative = reduces risk
            "top_10_concentration": 30,
            "anomaly_score": 25,
            "total_tax": 20,
            "honeypot_pattern_count": 10
        }
        
        score = 30  # Base score
        
        for feature, weight in weights.items():
            if feature in features:
                score += features[feature] * weight
        
        # Normalize to 0-100
        return max(0, min(100, score))
    
    def get_feature_importance(self, features: Dict[str, float]) -> Dict[str, float]:
        """Get feature importance scores"""
        # Mock: return top contributing features
        importance = {}
        
        if features.get("is_known_scam", 0) > 0:
            importance["is_known_scam"] = 1.0
        
        if features.get("lp_locked", 0) == 0:
            importance["no_lp_lock"] = 0.8
        
        if features.get("has_mint", 0) > 0:
            importance["has_mint_function"] = 0.7
        
        if features.get("top_10_concentration", 0) > 0.5:
            importance["high_concentration"] = 0.6
        
        return importance


# Global model instance
ml_model = MockMLModel()


async def predict(features: Dict[str, float], module_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Predict final risk score using ML model with CRITICAL ISSUE DETECTION
    
    Args:
        features: Extracted features from all modules
        module_results: Raw module results
        
    Returns:
        ML prediction result
    """
    try:
        # CRITICAL: Check for deal-breaker issues
        contract_security = module_results.get("contract_security", {})
        liquidity_pool = module_results.get("liquidity_pool", {})
        
        # Deal-breaker 1: No bytecode (scam indicator)
        if contract_security.get("risk_score", 0) >= 50:
            warnings = contract_security.get("warnings", [])
            if any("bytecode" in str(w).lower() or "obfuscated" in str(w).lower() for w in warnings):
                logger.warning("🚨 CRITICAL: Bytecode unavailable - forcing HIGH risk")
                return {
                    "risk_score": 75.0,  # Force HIGH risk
                    "feature_importance": {"bytecode_unavailable": 1.0},
                    "confidence": 90,
                    "reason": "Contract bytecode unavailable or obfuscated"
                }
        
        # Deal-breaker 2: Very low liquidity (<$10k) + no activity
        liq_risk = liquidity_pool.get("risk_score", 0)
        if liq_risk >= 60:
            transfer_anomaly = module_results.get("transfer_anomaly", {})
            if transfer_anomaly.get("risk_score", 0) >= 30:
                logger.warning("🚨 CRITICAL: Low liquidity + no activity = DEAD/SCAM")
                return {
                    "risk_score": 70.0,  # Force HIGH risk
                    "feature_importance": {"low_liquidity_no_activity": 1.0},
                    "confidence": 85,
                    "reason": "Very low liquidity with no trading activity"
                }
        
        # Calculate ML risk score (for non-critical cases)
        ml_risk_score = ml_model.predict(features)
        
        # Calculate WEIGHTED module scores (some modules more important)
        module_weights = {
            "contract_security": 3.0,     # Most important
            "liquidity_pool": 2.5,         # Very important
            "holder_analysis": 2.0,        # Important
            "transfer_anomaly": 1.5,       # Moderate
            "pattern_matching": 1.0        # Supporting
        }
        
        weighted_score = 0
        total_weight = 0
        
        for module_name, result in module_results.items():
            weight = module_weights.get(module_name, 1.0)
            score = result.get("risk_score", 50)
            weighted_score += score * weight
            total_weight += weight
        
        avg_module_score = weighted_score / total_weight if total_weight > 0 else 50
        
        # Adaptive weighting based on confidence
        # High confidence → trust ML more
        # Low confidence → trust modules more
        confidence = 60  # Base confidence
        
        if ml_risk_score > 70 and avg_module_score > 60:
            # Both agree it's high risk - high confidence
            confidence = 90
            final_score = 0.7 * ml_risk_score + 0.3 * avg_module_score
        elif abs(ml_risk_score - avg_module_score) < 10:
            # Close agreement - moderate confidence
            confidence = 75
            final_score = 0.6 * ml_risk_score + 0.4 * avg_module_score
        else:
            # Disagreement - trust modules more (they use real data)
            confidence = 50
            final_score = 0.3 * ml_risk_score + 0.7 * avg_module_score
        
        # Get feature importance
        feature_importance = ml_model.get_feature_importance(features)
        
        logger.info(f"ML risk: {ml_risk_score:.1f}, Module weighted: {avg_module_score:.1f}, Final: {final_score:.1f} (confidence: {confidence}%)")
        
        return {
            "risk_score": round(final_score, 2),
            "ml_score": round(ml_risk_score, 2),
            "module_average": round(avg_module_score, 2),
            "confidence": confidence,
            "feature_importance": feature_importance
        }
        
    except Exception as e:
        logger.error(f"ML prediction failed: {str(e)}")
        # Fallback to WEIGHTED module average
        module_weights = {
            "contract_security": 3.0,
            "liquidity_pool": 2.5,
            "holder_analysis": 2.0,
            "transfer_anomaly": 1.5,
            "pattern_matching": 1.0
        }
        
        weighted_score = 0
        total_weight = 0
        
        for module_name, result in module_results.items():
            weight = module_weights.get(module_name, 1.0)
            score = result.get("risk_score", 50)
            weighted_score += score * weight
            total_weight += weight
        
        fallback_score = weighted_score / total_weight if total_weight > 0 else 50
        
        return {
            "risk_score": round(fallback_score, 2),
            "ml_score": None,
            "module_average": round(fallback_score, 2),
            "confidence": 50,
            "feature_importance": {}
        }
