"""
Deep Learning Model
Neural Network for rug pull risk prediction using TensorFlow/Keras
"""
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

# Lazy imports for optional dependencies
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models, regularizers
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logger.warning("TensorFlow not available. Deep learning features disabled.")


class DeepLearningModel:
    """Deep Neural Network for rug pull detection"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.model_path = model_path or str(Path(__file__).parent.parent.parent / "data" / "models" / "deep_model.h5")
        self.input_dim = 40  # Number of features from FeatureExtractor (updated from 42)
        
        if TENSORFLOW_AVAILABLE:
            self._load_or_create_model()
        else:
            logger.warning("TensorFlow not installed. Using fallback model.")
    
    def _create_model(self):
        """
        Create a deep neural network architecture
        
        Architecture:
        - Input: 40 features
        - Hidden Layer 1: 128 neurons, ReLU, Dropout(0.3)
        - Hidden Layer 2: 64 neurons, ReLU, Dropout(0.3)
        - Hidden Layer 3: 32 neurons, ReLU, Dropout(0.2)
        - Hidden Layer 4: 16 neurons, ReLU
        - Output: 1 neuron, Sigmoid (0-1 probability)
        """
        if not TENSORFLOW_AVAILABLE:
            return None
        model = models.Sequential([
            layers.Input(shape=(self.input_dim,)),
            
            # First hidden layer with batch normalization
            layers.Dense(128, activation='relu', 
                        kernel_regularizer=regularizers.l2(0.001)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            # Second hidden layer
            layers.Dense(64, activation='relu',
                        kernel_regularizer=regularizers.l2(0.001)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            # Third hidden layer
            layers.Dense(32, activation='relu',
                        kernel_regularizer=regularizers.l2(0.001)),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            # Fourth hidden layer
            layers.Dense(16, activation='relu'),
            layers.Dropout(0.1),
            
            # Output layer (sigmoid for probability)
            layers.Dense(1, activation='sigmoid')
        ])
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'AUC', keras.metrics.Precision(), keras.metrics.Recall()]
        )
        
        logger.info("Created new deep learning model")
        return model
    
    def _load_or_create_model(self):
        """Load existing model or create new one"""
        if os.path.exists(self.model_path):
            try:
                self.model = keras.models.load_model(self.model_path)
                logger.info(f"✅ Loaded deep learning model from {self.model_path}")
            except Exception as e:
                logger.warning(f"Failed to load model: {e}. Creating new model.")
                # Create model directory if it doesn't exist
                os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
                self.model = self._create_model()
                # Save immediately to fix version mismatch
                self.model.save(self.model_path)
                logger.info(f"✅ Saved new model to {self.model_path}")
        else:
            logger.info("No existing model found. Creating new model.")
            # Create model directory if it doesn't exist
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            self.model = self._create_model()
            # Save the new model
            self.model.save(self.model_path)
            logger.info(f"✅ Saved new model to {self.model_path}")
    
    def predict(self, features: np.ndarray) -> float:
        """
        Predict rug pull probability
        
        Args:
            features: Feature vector (shape: (n_features,))
            
        Returns:
            Risk score (0-100)
        """
        if not TENSORFLOW_AVAILABLE or self.model is None:
            return self._fallback_predict(features)
        
        try:
            # Reshape for batch prediction
            if len(features.shape) == 1:
                features = features.reshape(1, -1)
            
            # Ensure correct input dimension
            if features.shape[1] != self.input_dim:
                logger.warning(f"Feature dimension mismatch. Expected {self.input_dim}, got {features.shape[1]}")
                # Pad or truncate
                if features.shape[1] < self.input_dim:
                    padding = np.zeros((features.shape[0], self.input_dim - features.shape[1]))
                    features = np.hstack([features, padding])
                else:
                    features = features[:, :self.input_dim]
            
            # Predict probability
            probability = self.model.predict(features, verbose=0)[0][0]
            
            # Convert to risk score (0-100)
            risk_score = float(probability * 100)
            
            logger.info(f"Deep learning prediction: {risk_score:.2f}")
            return risk_score
            
        except Exception as e:
            logger.error(f"Deep learning prediction failed: {e}")
            return self._fallback_predict(features)
    
    def _fallback_predict(self, features: np.ndarray) -> float:
        """Fallback prediction using simple weighted sum"""
        # Use key features with weights
        if len(features) < 10:
            return 50.0
        
        # Simple weighted scoring
        weights = np.array([
            3.0,  # contract_risk_score
            2.0,  # holder_risk_score
            2.5,  # liquidity_risk_score
            1.5,  # transfer_risk_score
            1.0,  # pattern_risk_score
            1.0,  # tokenomics_risk_score
            5.0,  # is_known_scam (very important)
            4.0,  # has_selfdestruct
            3.0,  # honeypot_pattern
            2.0,  # lp_locked (negative weight)
        ])
        
        relevant_features = features[:len(weights)]
        score = np.dot(relevant_features, weights) / weights.sum() * 100
        
        return float(np.clip(score, 0, 100))
    
    def get_confidence(self, features: np.ndarray) -> float:
        """
        Calculate prediction confidence
        
        Returns:
            Confidence score (0-100)
        """
        if not TENSORFLOW_AVAILABLE or self.model is None:
            return 50.0
        
        try:
            if len(features.shape) == 1:
                features = features.reshape(1, -1)
            
            # Predict probability
            prob = self.model.predict(features, verbose=0)[0][0]
            
            # Confidence is how far from 0.5 (uncertain)
            # prob close to 0 or 1 = high confidence
            # prob close to 0.5 = low confidence
            confidence = abs(prob - 0.5) * 2 * 100
            
            return float(confidence)
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return 50.0
    
    def explain_prediction(self, features: np.ndarray, feature_names: list) -> Dict[str, float]:
        """
        Explain prediction using gradient-based importance
        
        Returns:
            Feature importance dictionary
        """
        if not TENSORFLOW_AVAILABLE or self.model is None:
            return {}
        
        try:
            if len(features.shape) == 1:
                features = features.reshape(1, -1)
            
            # Convert to tensor
            features_tensor = tf.convert_to_tensor(features, dtype=tf.float32)
            
            # Calculate gradients
            with tf.GradientTape() as tape:
                tape.watch(features_tensor)
                prediction = self.model(features_tensor)
            
            # Get gradients (feature importance)
            gradients = tape.gradient(prediction, features_tensor)
            
            if gradients is not None:
                # Convert to numpy and get absolute values
                importance = np.abs(gradients.numpy()[0])
                
                # Normalize
                importance = importance / (importance.sum() + 1e-10)
                
                # Create dictionary with top features
                feature_importance = {}
                for i, name in enumerate(feature_names[:len(importance)]):
                    if importance[i] > 0.01:  # Only include significant features
                        feature_importance[name] = float(importance[i])
                
                # Sort by importance
                feature_importance = dict(sorted(
                    feature_importance.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:10])  # Top 10
                
                return feature_importance
            
        except Exception as e:
            logger.error(f"Explanation failed: {e}")
        
        return {}
    
    def save(self):
        """Save model to disk"""
        if TENSORFLOW_AVAILABLE and self.model is not None:
            try:
                self.model.save(self.model_path)
                logger.info(f"Model saved to {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to save model: {e}")
