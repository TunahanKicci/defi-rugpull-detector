"""
Quick test of ML ensemble system
"""
import asyncio
import logging
from modules.ml.feature_extractor import FeatureExtractor
from modules.ml.ensemble_model import EnsembleModel
from modules.h_ml_risk_scorer import predict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_ml_system():
    """Test the ML ensemble"""
    
    # Sample module results (simulating a risky token)
    module_results = {
        "contract_security": {
            "risk_score": 45,
            "has_bytecode": True,
            "is_verified": False,
            "has_selfdestruct": True,
            "has_delegatecall": False,
            "is_proxy": False
        },
        "holder_analysis": {
            "risk_score": 35,
            "top_10_concentration": 0.75,
            "top_holder_percentage": 45,
            "gini_coefficient": 0.92,
            "unique_holders": 150
        },
        "liquidity_pool": {
            "risk_score": 55,
            "is_locked": False,
            "liquidity_usd": 8500,
            "has_pair": True
        },
        "transfer_anomaly": {
            "risk_score": 40,
            "mint_count": 3,
            "burn_count": 0,
            "unique_senders": 50,
            "unique_receivers": 45,
            "anomaly_score": 0.6,
            "total_transfers": 120
        },
        "pattern_matching": {
            "risk_score": 50,
            "is_known_scam": False,
            "has_honeypot_pattern": True,
            "similarity_score": 0.3
        },
        "tokenomics": {
            "risk_score": 20,
            "total_supply": 1000000000,
            "has_tax": True,
            "buy_tax": 5,
            "sell_tax": 10
        }
    }
    
    logger.info("=" * 70)
    logger.info("TESTING ML ENSEMBLE SYSTEM")
    logger.info("=" * 70)
    
    # Test feature extraction
    logger.info("\n1. Testing Feature Extraction...")
    feature_extractor = FeatureExtractor()
    features = feature_extractor.extract(module_results)
    logger.info(f"✅ Extracted {len(features)} features")
    logger.info(f"Sample features: {list(features.keys())[:10]}")
    
    # Test ensemble prediction
    logger.info("\n2. Testing Ensemble Prediction...")
    result = await predict({}, module_results)
    
    logger.info("\n" + "=" * 70)
    logger.info("PREDICTION RESULTS")
    logger.info("=" * 70)
    logger.info(f"🎯 Final Risk Score: {result['risk_score']}")
    logger.info(f"📊 Risk Level: {result.get('risk_level', 'N/A')}")
    logger.info(f"🤖 ML Ensemble Score: {result.get('ml_ensemble_score', 'N/A')}")
    logger.info(f"📈 Module Weighted Score: {result.get('module_weighted_score', 'N/A')}")
    logger.info(f"🎯 Confidence: {result['confidence']}%")
    
    if result.get('models_used'):
        logger.info(f"\n✅ Models Used: {', '.join(result['models_used'])}")
    
    if result.get('model_predictions'):
        logger.info("\n📊 Individual Model Predictions:")
        for model, score in result['model_predictions'].items():
            logger.info(f"  - {model}: {score:.2f}")
    
    if result.get('feature_importance'):
        logger.info("\n🔍 Top Feature Importance:")
        for i, (feature, importance) in enumerate(list(result['feature_importance'].items())[:5], 1):
            logger.info(f"  {i}. {feature}: {importance:.4f}")
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ ML ENSEMBLE TEST COMPLETE")
    logger.info("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_ml_system())
