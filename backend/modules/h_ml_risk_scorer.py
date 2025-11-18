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
    Predict final risk score using ML model
    
    Args:
        features: Extracted features from all modules
        module_results: Raw module results
        
    Returns:
        ML prediction result
    """
    try:
        # Calculate ML risk score
        ml_risk_score = ml_model.predict(features)
        
        # Calculate average module score
        module_scores = [
            result.get("risk_score", 50)
            for result in module_results.values()
        ]
        avg_module_score = np.mean(module_scores) if module_scores else 50
        
        # Weighted combination: 70% ML, 30% module average
        final_score = 0.7 * ml_risk_score + 0.3 * avg_module_score
        
        # Get feature importance
        feature_importance = ml_model.get_feature_importance(features)
        
        logger.info(f"ML risk score: {ml_risk_score:.2f}, Module avg: {avg_module_score:.2f}, Final: {final_score:.2f}")
        
        return {
            "risk_score": round(final_score, 2),
            "ml_score": round(ml_risk_score, 2),
            "module_average": round(avg_module_score, 2),
            "feature_importance": feature_importance
        }
        
    except Exception as e:
        logger.error(f"ML prediction failed: {str(e)}")
        # Fallback to module average
        module_scores = [
            result.get("risk_score", 50)
            for result in module_results.values()
        ]
        fallback_score = np.mean(module_scores) if module_scores else 50
        
        return {
            "risk_score": round(fallback_score, 2),
            "ml_score": None,
            "module_average": round(fallback_score, 2),
            "feature_importance": {}
        }
