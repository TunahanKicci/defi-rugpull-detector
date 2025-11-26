"""
Ensemble Model
Combines multiple ML models (XGBoost, LightGBM, CatBoost, Deep Learning) for robust predictions
"""
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
import joblib

logger = logging.getLogger(__name__)

# Lazy imports
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logger.warning("XGBoost not available")

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    logger.warning("LightGBM not available")

try:
    import catboost as cb
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False
    logger.warning("CatBoost not available")

from .deep_model import DeepLearningModel


class EnsembleModel:
    """
    Ensemble of multiple ML models for robust rug pull detection
    
    Models:
    1. XGBoost - Gradient boosting
    2. LightGBM - Fast gradient boosting
    3. CatBoost - Categorical boosting
    4. Deep Neural Network - Deep learning
    
    Ensemble strategy: Weighted voting based on model confidence
    """
    
    def __init__(self, model_dir: Optional[str] = None):
        self.model_dir = model_dir or str(Path(__file__).parent.parent.parent / "data" / "models")
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Initialize models
        self.xgb_model = None
        self.lgb_model = None
        self.cat_model = None
        self.deep_model = DeepLearningModel()
        
        # Model weights (based on validation performance)
        self.weights = {
            'xgboost': 0.30,
            'lightgbm': 0.25,
            'catboost': 0.20,
            'deep': 0.25
        }
        
        self._load_or_create_models()
    
    def _create_xgboost_model(self):
        """Create XGBoost model"""
        if not XGBOOST_AVAILABLE:
            return None
        
        params = {
            'objective': 'binary:logistic',
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'min_child_weight': 3,
            'gamma': 0.1,
            'reg_alpha': 0.1,
            'reg_lambda': 1.0,
            'random_state': 42
        }
        
        model = xgb.XGBClassifier(**params)
        logger.info("Created XGBoost model")
        return model
    
    def _create_lightgbm_model(self):
        """Create LightGBM model"""
        if not LIGHTGBM_AVAILABLE:
            return None
        
        params = {
            'objective': 'binary',
            'metric': 'auc',
            'num_leaves': 31,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'min_child_samples': 20,
            'reg_alpha': 0.1,
            'reg_lambda': 1.0,
            'random_state': 42,
            'verbose': -1
        }
        
        model = lgb.LGBMClassifier(**params)
        logger.info("Created LightGBM model")
        return model
    
    def _create_catboost_model(self):
        """Create CatBoost model"""
        if not CATBOOST_AVAILABLE:
            return None
        
        params = {
            'iterations': 100,
            'learning_rate': 0.1,
            'depth': 6,
            'l2_leaf_reg': 3,
            'loss_function': 'Logloss',
            'eval_metric': 'AUC',
            'random_state': 42,
            'verbose': False
        }
        
        model = cb.CatBoostClassifier(**params)
        logger.info("Created CatBoost model")
        return model
    
    def _load_or_create_models(self):
        """Load existing models or create new ones"""
        # XGBoost
        xgb_path = os.path.join(self.model_dir, "xgboost_model.pkl")
        if os.path.exists(xgb_path):
            try:
                self.xgb_model = joblib.load(xgb_path)
                logger.info("Loaded XGBoost model")
            except Exception as e:
                logger.warning(f"Failed to load XGBoost: {e}")
                self.xgb_model = self._create_xgboost_model()
        else:
            self.xgb_model = self._create_xgboost_model()
        
        # LightGBM
        lgb_path = os.path.join(self.model_dir, "lightgbm_model.pkl")
        if os.path.exists(lgb_path):
            try:
                self.lgb_model = joblib.load(lgb_path)
                logger.info("Loaded LightGBM model")
            except Exception as e:
                logger.warning(f"Failed to load LightGBM: {e}")
                self.lgb_model = self._create_lightgbm_model()
        else:
            self.lgb_model = self._create_lightgbm_model()
        
        # CatBoost
        cat_path = os.path.join(self.model_dir, "catboost_model.pkl")
        if os.path.exists(cat_path):
            try:
                self.cat_model = joblib.load(cat_path)
                logger.info("Loaded CatBoost model")
            except Exception as e:
                logger.warning(f"Failed to load CatBoost: {e}")
                self.cat_model = self._create_catboost_model()
        else:
            self.cat_model = self._create_catboost_model()
    
    def predict(self, features: np.ndarray) -> Dict[str, Any]:
        """
        Ensemble prediction from all models
        
        Args:
            features: Feature vector
            
        Returns:
            Prediction result with ensemble score and individual model scores
        """
        if len(features.shape) == 1:
            features = features.reshape(1, -1)
        
        predictions = {}
        confidences = {}
        
        # XGBoost prediction
        if self.xgb_model is not None:
            try:
                xgb_proba = self.xgb_model.predict_proba(features)[0][1]
                predictions['xgboost'] = float(xgb_proba * 100)
                confidences['xgboost'] = abs(xgb_proba - 0.5) * 2
            except Exception as e:
                logger.error(f"XGBoost prediction failed: {e}")
        
        # LightGBM prediction
        if self.lgb_model is not None:
            try:
                lgb_proba = self.lgb_model.predict_proba(features)[0][1]
                predictions['lightgbm'] = float(lgb_proba * 100)
                confidences['lightgbm'] = abs(lgb_proba - 0.5) * 2
            except Exception as e:
                logger.error(f"LightGBM prediction failed: {e}")
        
        # CatBoost prediction
        if self.cat_model is not None:
            try:
                cat_proba = self.cat_model.predict_proba(features)[0][1]
                predictions['catboost'] = float(cat_proba * 100)
                confidences['catboost'] = abs(cat_proba - 0.5) * 2
            except Exception as e:
                logger.error(f"CatBoost prediction failed: {e}")
        
        # Deep Learning prediction
        try:
            deep_score = self.deep_model.predict(features)
            predictions['deep'] = float(deep_score)
            confidences['deep'] = self.deep_model.get_confidence(features) / 100
        except Exception as e:
            logger.error(f"Deep learning prediction failed: {e}")
        
        # Ensemble prediction (weighted average)
        if predictions:
            weighted_sum = 0
            total_weight = 0
            
            for model_name, score in predictions.items():
                weight = self.weights.get(model_name, 0.25)
                confidence = confidences.get(model_name, 0.5)
                
                # Adjust weight by confidence
                adjusted_weight = weight * (0.5 + confidence * 0.5)
                
                weighted_sum += score * adjusted_weight
                total_weight += adjusted_weight
            
            ensemble_score = weighted_sum / total_weight if total_weight > 0 else 50.0
            
            # Calculate ensemble confidence (average of individual confidences)
            avg_confidence = np.mean(list(confidences.values())) * 100 if confidences else 50.0
            
            # Check for agreement (all models close to each other = high confidence)
            if len(predictions) >= 2:
                scores = list(predictions.values())
                std = np.std(scores)
                if std < 10:  # Low variance = high agreement
                    avg_confidence = min(avg_confidence * 1.2, 95)
                elif std > 30:  # High variance = low agreement
                    avg_confidence = max(avg_confidence * 0.8, 40)
            
            logger.info(f"Ensemble prediction: {ensemble_score:.2f} (confidence: {avg_confidence:.1f}%)")
            logger.info(f"Individual predictions: {predictions}")
            
            return {
                'ensemble_score': float(ensemble_score),
                'confidence': float(avg_confidence),
                'model_predictions': predictions,
                'model_confidences': {k: float(v * 100) for k, v in confidences.items()},
                'models_used': list(predictions.keys())
            }
        else:
            logger.warning("No models available for prediction")
            return {
                'ensemble_score': 50.0,
                'confidence': 30.0,
                'model_predictions': {},
                'model_confidences': {},
                'models_used': []
            }
    
    def get_feature_importance(self, feature_names: List[str]) -> Dict[str, float]:
        """
        Get aggregated feature importance from all models
        
        Returns:
            Feature importance dictionary
        """
        importance_dict = {}
        
        # XGBoost importance
        if self.xgb_model is not None and hasattr(self.xgb_model, 'feature_importances_'):
            try:
                xgb_imp = self.xgb_model.feature_importances_
                for i, name in enumerate(feature_names[:len(xgb_imp)]):
                    importance_dict[name] = importance_dict.get(name, 0) + xgb_imp[i] * self.weights['xgboost']
            except Exception as e:
                logger.error(f"XGBoost importance failed: {e}")
        
        # LightGBM importance
        if self.lgb_model is not None and hasattr(self.lgb_model, 'feature_importances_'):
            try:
                lgb_imp = self.lgb_model.feature_importances_
                lgb_imp = lgb_imp / (lgb_imp.sum() + 1e-10)  # Normalize
                for i, name in enumerate(feature_names[:len(lgb_imp)]):
                    importance_dict[name] = importance_dict.get(name, 0) + lgb_imp[i] * self.weights['lightgbm']
            except Exception as e:
                logger.error(f"LightGBM importance failed: {e}")
        
        # CatBoost importance
        if self.cat_model is not None and hasattr(self.cat_model, 'get_feature_importance'):
            try:
                cat_imp = self.cat_model.get_feature_importance()
                cat_imp = cat_imp / (cat_imp.sum() + 1e-10)  # Normalize
                for i, name in enumerate(feature_names[:len(cat_imp)]):
                    importance_dict[name] = importance_dict.get(name, 0) + cat_imp[i] * self.weights['catboost']
            except Exception as e:
                logger.error(f"CatBoost importance failed: {e}")
        
        # Normalize total importance
        if importance_dict:
            total = sum(importance_dict.values())
            importance_dict = {k: v / total for k, v in importance_dict.items()}
            
            # Sort and return top features
            importance_dict = dict(sorted(
                importance_dict.items(),
                key=lambda x: x[1],
                reverse=True
            )[:15])  # Top 15
        
        return importance_dict
    
    def save_models(self):
        """Save all models to disk"""
        # Save tree-based models
        if self.xgb_model is not None:
            try:
                joblib.dump(self.xgb_model, os.path.join(self.model_dir, "xgboost_model.pkl"))
                logger.info("Saved XGBoost model")
            except Exception as e:
                logger.error(f"Failed to save XGBoost: {e}")
        
        if self.lgb_model is not None:
            try:
                joblib.dump(self.lgb_model, os.path.join(self.model_dir, "lightgbm_model.pkl"))
                logger.info("Saved LightGBM model")
            except Exception as e:
                logger.error(f"Failed to save LightGBM: {e}")
        
        if self.cat_model is not None:
            try:
                joblib.dump(self.cat_model, os.path.join(self.model_dir, "catboost_model.pkl"))
                logger.info("Saved CatBoost model")
            except Exception as e:
                logger.error(f"Failed to save CatBoost: {e}")
        
        # Save deep learning model
        self.deep_model.save()
