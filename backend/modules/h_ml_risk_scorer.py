"""
Module H: ML Risk Scorer
Combines all features and predicts final risk score using trained ML models
"""
import logging
from typing import Dict, Any, List, Optional
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

# Import ML modules
try:
    from modules.ml.ensemble_model import EnsembleModel
    from modules.ml.feature_extractor import FeatureExtractor
    ML_AVAILABLE = True
    logger.info("[OK] ML modules imported successfully")
except ImportError as e:
    ML_AVAILABLE = False
    logger.warning(f"⚠️ ML modules not available: {e}")


class MLRiskScorer:
    """ML-based risk scorer using trained ensemble model"""
    
    def __init__(self):
        self.ensemble_model: Optional[EnsembleModel] = None
        self.feature_extractor = FeatureExtractor()
        self._load_models()
    
    def _load_models(self):
        """Load trained ML models"""
        if not ML_AVAILABLE:
            logger.warning("ML modules not available, using fallback scoring")
            return
        
        try:
            models_dir = Path(__file__).parent.parent / "data" / "models"
            logger.info(f"[SEARCH] Looking for models in: {models_dir}")
            
            if not models_dir.exists():
                logger.warning(f"❌ Models directory not found: {models_dir}")
                return
            
            # List available model files
            model_files = list(models_dir.glob("*.pkl")) + list(models_dir.glob("*.h5"))
            logger.info(f"[FILES] Found model files: {[f.name for f in model_files]}")
            
            # Load ensemble model
            logger.info("[INIT] Initializing EnsembleModel...")
            self.ensemble_model = EnsembleModel(model_dir=str(models_dir))  # Fixed: model_dir not models_dir
            logger.info(f"[OK] Successfully loaded ML ensemble model from {models_dir}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load ML models: {e}", exc_info=True)
            self.ensemble_model = None
    
    def predict(self, module_results: Dict[str, Dict[str, Any]]) -> float:
        """
        Predict risk score using ML model
        
        Args:
            module_results: Results from all analysis modules
            
        Returns:
            Risk score (0-100)
        """
        if self.ensemble_model is None:
            # Fallback to weighted average
            return self._fallback_prediction(module_results)
        
        try:
            # Extract features as dict
            features_dict = self.feature_extractor.extract(module_results)
            
            # Convert to numpy array
            features_array = self.feature_extractor.get_feature_vector(features_dict)
            
            # Get ML prediction
            ml_result = self.ensemble_model.predict(features_array)
            
            # Extract risk score from result dict
            if isinstance(ml_result, dict):
                ml_risk = ml_result.get('ensemble_score', ml_result.get('risk_score', 50.0))
            else:
                ml_risk = float(ml_result)
            
            logger.info(f"[ML] Prediction: {ml_risk:.1f}")
            return ml_risk
            
        except Exception as e:
            logger.error(f"ML prediction failed: {e}", exc_info=True)
            return self._fallback_prediction(module_results)
    
    def _fallback_prediction(self, module_results: Dict[str, Dict[str, Any]]) -> float:
        """Fallback weighted average when ML not available"""
        weights = {
            "contract_security": 3.0,
            "liquidity_pool": 2.5,
            "holder_analysis": 2.0,
            "transfer_anomaly": 1.5,
            "pattern_matching": 1.0,
            "tokenomics": 1.0
        }
        
        weighted_score = 0
        total_weight = 0
        
        for module_name, result in module_results.items():
            weight = weights.get(module_name, 1.0)
            score = result.get("risk_score", 50)
            weighted_score += score * weight
            total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 50.0
    
    def get_feature_importance(self, module_results: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """Get feature importance from model"""
        if self.ensemble_model is None:
            return {}
        
        try:
            features = self.feature_extractor.extract(module_results)
            # Note: Feature importance would come from model internals
            # For now return empty dict
            return {}
        except Exception as e:
            logger.error(f"Failed to get feature importance: {e}")
            return {}


# Global model instance
ml_scorer = MLRiskScorer()


async def predict(features: Dict[str, float], module_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Predict final risk score using ML model with CRITICAL ISSUE DETECTION
    
    Args:
        features: Extracted features from all modules (unused, kept for compatibility)
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
                    "risk_score": 75.0,
                    "ml_score": 75.0,
                    "module_average": 75.0,
                    "confidence": 90,
                    "feature_importance": {"bytecode_unavailable": 1.0},
                    "reason": "Contract bytecode unavailable or obfuscated"
                }
        
        # Deal-breaker 2: Very low liquidity (<$10k) + no activity
        liq_risk = liquidity_pool.get("risk_score", 0)
        if liq_risk >= 60:
            transfer_anomaly = module_results.get("transfer_anomaly", {})
            if transfer_anomaly.get("risk_score", 0) >= 30:
                logger.warning("🚨 CRITICAL: Low liquidity + no activity = DEAD/SCAM")
                return {
                    "risk_score": 70.0,
                    "ml_score": 70.0,
                    "module_average": 70.0,
                    "confidence": 85,
                    "feature_importance": {"low_liquidity_no_activity": 1.0},
                    "reason": "Very low liquidity with no trading activity"
                }
        
        # Get ML prediction
        ml_risk_score = ml_scorer.predict(module_results)
        
        # Calculate WEIGHTED module scores
        module_weights = {
            "contract_security": 3.0,
            "liquidity_pool": 2.5,
            "holder_analysis": 2.0,
            "transfer_anomaly": 1.5,
            "pattern_matching": 1.0,
            "tokenomics": 1.0
        }
        
        weighted_score = 0
        total_weight = 0
        
        for module_name, result in module_results.items():
            weight = module_weights.get(module_name, 1.0)
            score = result.get("risk_score", 50)
            weighted_score += score * weight
            total_weight += weight
        
        avg_module_score = weighted_score / total_weight if total_weight > 0 else 50
        
        # Adaptive weighting based on agreement
        confidence = 60
        
        if ml_risk_score > 70 and avg_module_score > 60:
            # Both agree it's high risk
            confidence = 90
            final_score = 0.7 * ml_risk_score + 0.3 * avg_module_score
        elif abs(ml_risk_score - avg_module_score) < 10:
            # Close agreement
            confidence = 75
            final_score = 0.6 * ml_risk_score + 0.4 * avg_module_score
        else:
            # Disagreement - trust modules more
            confidence = 50
            final_score = 0.3 * ml_risk_score + 0.7 * avg_module_score
        
        # Get feature importance
        feature_importance = ml_scorer.get_feature_importance(module_results)
        
        logger.info(f"ML risk: {ml_risk_score:.1f}, Module weighted: {avg_module_score:.1f}, Final: {final_score:.1f} (confidence: {confidence}%)")
        
        return {
            "risk_score": round(final_score, 2),
            "ml_score": round(ml_risk_score, 2),
            "module_average": round(avg_module_score, 2),
            "confidence": confidence,
            "feature_importance": feature_importance
        }
        
    except Exception as e:
        logger.error(f"ML prediction failed: {str(e)}", exc_info=True)
        
        # Fallback to weighted module average
        module_weights = {
            "contract_security": 3.0,
            "liquidity_pool": 2.5,
            "holder_analysis": 2.0,
            "transfer_anomaly": 1.5,
            "pattern_matching": 1.0,
            "tokenomics": 1.0
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
