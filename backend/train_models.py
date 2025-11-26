"""
Model Training Script
Train ensemble ML models on historical rug pull data

Usage:
    python train_models.py --data data/training_data.csv
"""
import logging
import argparse
import os
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import ML components
from modules.ml.feature_extractor import FeatureExtractor
from modules.ml.ensemble_model import EnsembleModel


def load_training_data(data_path: str) -> tuple:
    """
    Load and prepare training data
    
    Expected CSV format:
    - Features: contract_risk_score, holder_risk_score, liquidity_risk_score, etc.
    - Target: is_rugpull (0 or 1)
    
    Returns:
        X_train, X_test, y_train, y_test
    """
    logger.info(f"Loading training data from {data_path}")
    
    if not os.path.exists(data_path):
        logger.error(f"Data file not found: {data_path}")
        return None, None, None, None
    
    # Load CSV
    df = pd.read_csv(data_path)
    
    logger.info(f"Loaded {len(df)} samples")
    logger.info(f"Columns: {list(df.columns)}")
    
    # Separate features and target
    if 'is_rugpull' not in df.columns:
        logger.error("Target column 'is_rugpull' not found")
        return None, None, None, None
    
    X = df.drop('is_rugpull', axis=1)
    y = df['is_rugpull']
    
    logger.info(f"Features: {X.shape[1]}, Samples: {len(X)}")
    logger.info(f"Class distribution: Rugpull={sum(y)}, Safe={len(y)-sum(y)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    logger.info(f"Train: {len(X_train)}, Test: {len(X_test)}")
    
    return X_train, X_test, y_train, y_test


def train_ensemble(X_train, y_train, X_test, y_test):
    """Train ensemble model"""
    logger.info("Initializing ensemble model...")
    ensemble = EnsembleModel()
    
    # Convert to numpy
    X_train_np = X_train.values if isinstance(X_train, pd.DataFrame) else X_train
    X_test_np = X_test.values if isinstance(X_test, pd.DataFrame) else X_test
    y_train_np = y_train.values if isinstance(y_train, pd.Series) else y_train
    y_test_np = y_test.values if isinstance(y_test, pd.Series) else y_test
    
    # Train XGBoost
    if ensemble.xgb_model is not None:
        logger.info("Training XGBoost...")
        ensemble.xgb_model.fit(X_train_np, y_train_np)
        
        y_pred = ensemble.xgb_model.predict(X_test_np)
        y_proba = ensemble.xgb_model.predict_proba(X_test_np)[:, 1]
        
        logger.info(f"XGBoost - Accuracy: {accuracy_score(y_test_np, y_pred):.4f}")
        logger.info(f"XGBoost - Precision: {precision_score(y_test_np, y_pred):.4f}")
        logger.info(f"XGBoost - Recall: {recall_score(y_test_np, y_pred):.4f}")
        logger.info(f"XGBoost - F1: {f1_score(y_test_np, y_pred):.4f}")
        logger.info(f"XGBoost - ROC AUC: {roc_auc_score(y_test_np, y_proba):.4f}")
    
    # Train LightGBM
    if ensemble.lgb_model is not None:
        logger.info("Training LightGBM...")
        ensemble.lgb_model.fit(X_train_np, y_train_np)
        
        y_pred = ensemble.lgb_model.predict(X_test_np)
        y_proba = ensemble.lgb_model.predict_proba(X_test_np)[:, 1]
        
        logger.info(f"LightGBM - Accuracy: {accuracy_score(y_test_np, y_pred):.4f}")
        logger.info(f"LightGBM - Precision: {precision_score(y_test_np, y_pred):.4f}")
        logger.info(f"LightGBM - Recall: {recall_score(y_test_np, y_pred):.4f}")
        logger.info(f"LightGBM - F1: {f1_score(y_test_np, y_pred):.4f}")
        logger.info(f"LightGBM - ROC AUC: {roc_auc_score(y_test_np, y_proba):.4f}")
    
    # Train CatBoost
    if ensemble.cat_model is not None:
        logger.info("Training CatBoost...")
        ensemble.cat_model.fit(X_train_np, y_train_np)
        
        y_pred = ensemble.cat_model.predict(X_test_np)
        y_proba = ensemble.cat_model.predict_proba(X_test_np)[:, 1]
        
        logger.info(f"CatBoost - Accuracy: {accuracy_score(y_test_np, y_pred):.4f}")
        logger.info(f"CatBoost - Precision: {precision_score(y_test_np, y_pred):.4f}")
        logger.info(f"CatBoost - Recall: {recall_score(y_test_np, y_pred):.4f}")
        logger.info(f"CatBoost - F1: {f1_score(y_test_np, y_pred):.4f}")
        logger.info(f"CatBoost - ROC AUC: {roc_auc_score(y_test_np, y_proba):.4f}")
    
    # Train Deep Learning (if enough data)
    if len(X_train) >= 100:
        logger.info("Training Deep Neural Network...")
        
        # Note: This is a simplified training. For production, use proper training loop
        # with validation set, early stopping, etc.
        try:
            import tensorflow as tf
            from tensorflow import keras
            
            # Prepare data
            X_train_scaled = (X_train_np - X_train_np.mean(axis=0)) / (X_train_np.std(axis=0) + 1e-10)
            X_test_scaled = (X_test_np - X_train_np.mean(axis=0)) / (X_train_np.std(axis=0) + 1e-10)
            
            # Train
            history = ensemble.deep_model.model.fit(
                X_train_scaled, y_train_np,
                validation_split=0.2,
                epochs=50,
                batch_size=32,
                verbose=1,
                callbacks=[
                    keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
                    keras.callbacks.ReduceLROnPlateau(patience=5, factor=0.5)
                ]
            )
            
            # Evaluate
            y_pred_proba = ensemble.deep_model.model.predict(X_test_scaled, verbose=0)
            y_pred = (y_pred_proba > 0.5).astype(int).flatten()
            
            logger.info(f"Deep NN - Accuracy: {accuracy_score(y_test_np, y_pred):.4f}")
            logger.info(f"Deep NN - Precision: {precision_score(y_test_np, y_pred):.4f}")
            logger.info(f"Deep NN - Recall: {recall_score(y_test_np, y_pred):.4f}")
            logger.info(f"Deep NN - F1: {f1_score(y_test_np, y_pred):.4f}")
            logger.info(f"Deep NN - ROC AUC: {roc_auc_score(y_test_np, y_pred_proba):.4f}")
            
        except Exception as e:
            logger.error(f"Deep learning training failed: {e}")
    else:
        logger.warning("Not enough data for deep learning training (need at least 100 samples)")
    
    # Evaluate ensemble
    logger.info("\n" + "="*50)
    logger.info("ENSEMBLE EVALUATION")
    logger.info("="*50)
    
    ensemble_predictions = []
    for i in range(len(X_test)):
        features = X_test_np[i:i+1]
        result = ensemble.predict(features)
        ensemble_predictions.append(result['ensemble_score'] / 100)  # Convert to probability
    
    y_pred_ensemble = (np.array(ensemble_predictions) > 0.5).astype(int)
    
    logger.info(f"Ensemble - Accuracy: {accuracy_score(y_test_np, y_pred_ensemble):.4f}")
    logger.info(f"Ensemble - Precision: {precision_score(y_test_np, y_pred_ensemble):.4f}")
    logger.info(f"Ensemble - Recall: {recall_score(y_test_np, y_pred_ensemble):.4f}")
    logger.info(f"Ensemble - F1: {f1_score(y_test_np, y_pred_ensemble):.4f}")
    logger.info(f"Ensemble - ROC AUC: {roc_auc_score(y_test_np, ensemble_predictions):.4f}")
    
    # Save models
    logger.info("\nSaving models...")
    ensemble.save_models()
    logger.info("✅ All models saved successfully")
    
    return ensemble


def generate_sample_data(output_path: str, n_samples: int = 1000):
    """Generate sample training data for demonstration"""
    logger.info(f"Generating {n_samples} sample training data...")
    
    np.random.seed(42)
    
    # Generate synthetic features
    data = {
        'contract_risk_score': np.random.uniform(0, 1, n_samples),
        'holder_risk_score': np.random.uniform(0, 1, n_samples),
        'liquidity_risk_score': np.random.uniform(0, 1, n_samples),
        'transfer_risk_score': np.random.uniform(0, 1, n_samples),
        'pattern_risk_score': np.random.uniform(0, 1, n_samples),
        'has_selfdestruct': np.random.randint(0, 2, n_samples),
        'lp_locked': np.random.randint(0, 2, n_samples),
        'top_10_concentration': np.random.uniform(0, 1, n_samples),
        'gini_coefficient': np.random.uniform(0.3, 1, n_samples),
        'mint_count': np.random.uniform(0, 1, n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Generate target based on features (simulate rug pulls)
    df['is_rugpull'] = (
        (df['contract_risk_score'] > 0.7) |
        (df['liquidity_risk_score'] > 0.8) |
        ((df['has_selfdestruct'] == 1) & (df['lp_locked'] == 0)) |
        (df['top_10_concentration'] > 0.9)
    ).astype(int)
    
    # Add some noise
    noise_indices = np.random.choice(len(df), size=int(len(df) * 0.1), replace=False)
    df.loc[noise_indices, 'is_rugpull'] = 1 - df.loc[noise_indices, 'is_rugpull']
    
    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    logger.info(f"✅ Sample data saved to {output_path}")
    logger.info(f"Rugpulls: {df['is_rugpull'].sum()}, Safe: {len(df) - df['is_rugpull'].sum()}")


def main():
    parser = argparse.ArgumentParser(description='Train ML models for rug pull detection')
    parser.add_argument('--data', type=str, help='Path to training data CSV')
    parser.add_argument('--generate', action='store_true', help='Generate sample data')
    parser.add_argument('--samples', type=int, default=1000, help='Number of samples to generate')
    
    args = parser.parse_args()
    
    # Generate sample data if requested
    if args.generate:
        output_path = args.data or 'data/training_data.csv'
        generate_sample_data(output_path, args.samples)
        return
    
    # Load training data
    if not args.data:
        logger.error("Please provide --data path or use --generate to create sample data")
        return
    
    X_train, X_test, y_train, y_test = load_training_data(args.data)
    
    if X_train is None:
        logger.error("Failed to load training data")
        return
    
    # Train ensemble
    ensemble = train_ensemble(X_train, y_train, X_test, y_test)
    
    logger.info("\n✅ Training complete!")


if __name__ == '__main__':
    main()
