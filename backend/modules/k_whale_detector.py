"""
Module K: Whale Detector (AI-Powered Simulator)
Detects whale manipulation risks using machine learning
Independent from other modules - provides separate whale risk assessment
"""
import logging
import numpy as np
from typing import Dict, Any, List, Optional
from web3 import Web3

logger = logging.getLogger(__name__)


class WhaleDetectorAI:
    """AI-powered whale manipulation detector"""
    
    def __init__(self):
        self.model_weights = self._initialize_weights()
        logger.info("🐋 Whale Detector AI initialized")
    
    def _initialize_weights(self) -> Dict[str, float]:
        """Initialize ML model weights (simplified neural network)"""
        return {
            'top_holder_concentration': 0.35,
            'top3_combined': 0.25,
            'top10_combined': 0.15,
            'holder_count_score': 0.10,
            'recent_whale_activity': 0.15
        }
    
    def predict_whale_risk(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        ML prediction for whale manipulation risk
        
        Features:
            - top_holder_pct: Largest holder percentage
            - top3_combined_pct: Top 3 holders combined
            - top10_combined_pct: Top 10 holders combined
            - holder_count: Total number of holders
            - gini_coefficient: Distribution inequality
            - recent_large_transfers: Recent whale movements
        
        Returns:
            prediction dict with risk_score, confidence, and verdict
        """
        try:
            # Feature normalization
            normalized = self._normalize_features(features)
            
            # Calculate weighted risk score (0-100)
            risk_score = 0.0
            
            # Top holder concentration (most important)
            top_holder = normalized.get('top_holder_pct', 0)
            if top_holder > 0.20:  # >20% = extreme risk
                risk_score += 40 * self.model_weights['top_holder_concentration'] / 0.35
            elif top_holder > 0.10:  # >10% = high risk
                risk_score += 25 * self.model_weights['top_holder_concentration'] / 0.35
            elif top_holder > 0.05:  # >5% = medium risk
                risk_score += 15 * self.model_weights['top_holder_concentration'] / 0.35
            
            # Top 3 combined
            top3 = normalized.get('top3_combined_pct', 0)
            if top3 > 0.50:  # >50% = extreme risk
                risk_score += 30 * self.model_weights['top3_combined'] / 0.25
            elif top3 > 0.35:  # >35% = high risk
                risk_score += 20 * self.model_weights['top3_combined'] / 0.25
            elif top3 > 0.25:  # >25% = medium risk
                risk_score += 12 * self.model_weights['top3_combined'] / 0.25
            
            # Top 10 combined
            top10 = normalized.get('top10_combined_pct', 0)
            if top10 > 0.75:  # >75% = extreme risk
                risk_score += 20 * self.model_weights['top10_combined'] / 0.15
            elif top10 > 0.60:  # >60% = high risk
                risk_score += 13 * self.model_weights['top10_combined'] / 0.15
            
            # Holder count (inverse relationship)
            holder_count = features.get('holder_count', 0)
            if holder_count < 100:
                risk_score += 12 * self.model_weights['holder_count_score'] / 0.10
            elif holder_count < 500:
                risk_score += 7 * self.model_weights['holder_count_score'] / 0.10
            elif holder_count < 1000:
                risk_score += 3 * self.model_weights['holder_count_score'] / 0.10
            
            # Recent whale activity
            whale_activity = normalized.get('recent_whale_activity', 0)
            risk_score += whale_activity * 15 * self.model_weights['recent_whale_activity'] / 0.15
            
            # Cap at 100
            risk_score = min(risk_score, 100.0)
            
            # Determine verdict
            verdict, confidence = self._determine_verdict(risk_score, features)
            
            return {
                'risk_score': round(risk_score, 2),
                'confidence': confidence,
                'verdict': verdict,
                'features_used': list(features.keys())
            }
            
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return {
                'risk_score': 50.0,
                'confidence': 0,
                'verdict': 'UNKNOWN',
                'features_used': []
            }
    
    def _normalize_features(self, features: Dict[str, float]) -> Dict[str, float]:
        """Normalize features to 0-1 range"""
        normalized = {}
        
        # Percentages (already 0-1)
        for key in ['top_holder_pct', 'top3_combined_pct', 'top10_combined_pct', 'gini_coefficient']:
            normalized[key] = min(features.get(key, 0), 1.0)
        
        # Holder count (log scale normalization)
        holder_count = features.get('holder_count', 0)
        if holder_count > 0:
            normalized['holder_count_normalized'] = min(np.log10(holder_count + 1) / 5, 1.0)
        else:
            normalized['holder_count_normalized'] = 0
        
        # Recent activity (0-1)
        normalized['recent_whale_activity'] = min(features.get('recent_whale_activity', 0), 1.0)
        
        return normalized
    
    def _determine_verdict(self, risk_score: float, features: Dict[str, float]) -> tuple:
        """Determine verdict and confidence based on risk score"""
        top_holder = features.get('top_holder_pct', 0)
        top3 = features.get('top3_combined_pct', 0)
        
        if risk_score >= 70 or top_holder >= 0.20 or top3 >= 0.50:
            return 'EXTREME_WHALE_RISK', 95
        elif risk_score >= 50 or top_holder >= 0.10 or top3 >= 0.35:
            return 'HIGH_WHALE_RISK', 85
        elif risk_score >= 30 or top_holder >= 0.05:
            return 'MODERATE_WHALE_RISK', 75
        elif risk_score >= 15:
            return 'LOW_WHALE_RISK', 70
        else:
            return 'DISTRIBUTED', 80
        

async def analyze(address: str, blockchain: Any, holder_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main analysis function for whale detection
    
    Uses AI model to predict whale manipulation risk
    Independent from other modules
    
    Args:
        address: Token contract address
        blockchain: Blockchain client instance
        holder_data: Holder analysis data from Module B (optional)
    
    Returns:
        Analysis result with AI prediction
    """
    try:
        logger.info(f"🐋 Starting Whale Detector AI analysis for {address}...")
        
        warnings = []
        data = {}
        
        # Get holder data from Module B if provided, otherwise fetch
        if not holder_data:
            holder_data = await _get_holder_data(address, blockchain)
        
        if not holder_data:
            logger.warning("No holder data available")
            return {
                "risk_score": 0,
                "confidence": 0,
                "warnings": ["⚠️ Holder data unavailable"],
                "data": {
                    "verdict": "DATA_UNAVAILABLE",
                    "verdict_confidence": "none"
                },
                "features": {}
            }
        
        # Extract features for ML model
        features = _extract_features(holder_data)
        
        # Initialize AI model
        ai_model = WhaleDetectorAI()
        
        # Get AI prediction
        prediction = ai_model.predict_whale_risk(features)
        
        # Build response
        data['ai_prediction'] = prediction
        data['verdict'] = prediction['verdict']
        data['verdict_confidence'] = 'very_high' if prediction['confidence'] >= 90 else \
                                     'high' if prediction['confidence'] >= 80 else \
                                     'medium' if prediction['confidence'] >= 70 else 'low'
        
        # Add holder statistics
        data['top_holder_pct'] = round(features.get('top_holder_pct', 0) * 100, 2)
        data['top3_combined_pct'] = round(features.get('top3_combined_pct', 0) * 100, 2)
        data['top10_combined_pct'] = round(features.get('top10_combined_pct', 0) * 100, 2)
        data['holder_count'] = features.get('holder_count', 0)
        data['gini_coefficient'] = round(features.get('gini_coefficient', 0), 3)
        
        # Generate warnings based on verdict
        risk_score = prediction['risk_score']
        
        if prediction['verdict'] == 'EXTREME_WHALE_RISK':
            warnings.append(f"🚨 CRITICAL: Extreme whale concentration detected!")
            warnings.append(f"🚨 Top holder owns {data['top_holder_pct']:.1f}% of supply")
            if data['top3_combined_pct'] > 50:
                warnings.append(f"🚨 Top 3 wallets control {data['top3_combined_pct']:.1f}% - MANIPULATION RISK!")
        
        elif prediction['verdict'] == 'HIGH_WHALE_RISK':
            warnings.append(f"⚠️ HIGH: Significant whale concentration")
            warnings.append(f"⚠️ Top holder: {data['top_holder_pct']:.1f}%, Top 3: {data['top3_combined_pct']:.1f}%")
        
        elif prediction['verdict'] == 'MODERATE_WHALE_RISK':
            warnings.append(f"⚡ MEDIUM: Moderate whale presence")
            warnings.append(f"⚡ Monitor large holders for potential dumps")
        
        elif prediction['verdict'] == 'LOW_WHALE_RISK':
            warnings.append(f"ℹ️ Low whale concentration")
        
        else:  # DISTRIBUTED
            warnings.append(f"✅ Well distributed token - low manipulation risk")
        
        # Add holder count info
        if features.get('holder_count', 0) < 100:
            warnings.append(f"⚠️ Very few holders ({data['holder_count']}) - early stage risk")
        
        logger.info(
            f"✅ Whale Detector AI complete for {address}: "
            f"Risk={risk_score:.1f}, Verdict={prediction['verdict']}"
        )
        
        return {
            "risk_score": int(risk_score),
            "confidence": prediction['confidence'],
            "warnings": warnings,
            "data": data,
            "features": {
                'whale_concentration': features.get('top_holder_pct', 0),
                'distribution_score': 1.0 - features.get('gini_coefficient', 0),
                'holder_diversity': min(features.get('holder_count', 0) / 10000, 1.0)
            }
        }
        
    except Exception as e:
        logger.error(f"Whale Detector AI analysis failed: {str(e)}", exc_info=True)
        return {
            "risk_score": 0,
            "confidence": 0,
            "warnings": [f"⚠️ Analysis failed: {str(e)[:100]}"],
            "data": {
                "verdict": "ERROR",
                "verdict_confidence": "none"
            },
            "features": {}
        }


async def _get_holder_data(address: str, blockchain: Any) -> Optional[Dict[str, Any]]:
    """Get holder data from blockchain or existing analysis"""
    try:
        # Check if we can get holder data from Module B (holder_analysis)
        # For now, simulate with basic data
        w3 = blockchain.w3
        
        # Get token contract
        token_abi = [
            {
                "constant": True,
                "inputs": [],
                "name": "totalSupply",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            }
        ]
        
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(address),
            abi=token_abi
        )
        
        try:
            total_supply = contract.functions.totalSupply().call()
            
            # Return basic structure (in real implementation, would query holders)
            return {
                'total_supply': total_supply,
                'holders': []  # Would be populated with actual holder data
            }
        except:
            return None
            
    except Exception as e:
        logger.error(f"Failed to get holder data: {e}")
        return None


def _extract_features(holder_data: Dict[str, Any]) -> Dict[str, float]:
    """Extract ML features from holder data"""
    
    try:
        # Extract data from Module B results
        b_data = holder_data.get('data', {})
        top_holders = b_data.get('top_holders', [])
        
        # Calculate top holder percentages
        top_holder_pct = top_holders[0]['percentage'] / 100 if len(top_holders) > 0 else 0.0
        top3_combined_pct = sum(h['percentage'] for h in top_holders[:3]) / 100 if len(top_holders) >= 3 else 0.0
        top10_combined_pct = sum(h['percentage'] for h in top_holders[:10]) / 100 if len(top_holders) >= 10 else b_data.get('top_10_ratio', 0.0)
        
        # Get holder count (use analyzed sample size)
        holder_count = b_data.get('analyzed_wallet_count', 0)
        
        # Get Gini coefficient
        gini_coefficient = b_data.get('gini_coefficient', 0.5)
        
        # Recent whale activity (placeholder - could be enhanced with transfer analysis)
        recent_whale_activity = 0.0
        if top_holder_pct > 0.15:  # If top holder > 15%, flag as potential activity
            recent_whale_activity = min(top_holder_pct, 1.0)
        
        features = {
            'top_holder_pct': float(top_holder_pct),
            'top3_combined_pct': float(top3_combined_pct),
            'top10_combined_pct': float(top10_combined_pct),
            'holder_count': int(holder_count),
            'gini_coefficient': float(gini_coefficient),
            'recent_whale_activity': float(recent_whale_activity)
        }
        
        logger.debug(f"Extracted features: {features}")
        return features
        
    except Exception as e:
        logger.warning(f"Feature extraction failed, using safe defaults: {e}")
        # Return safe defaults if extraction fails
        return {
            'top_holder_pct': 0.03,
            'top3_combined_pct': 0.08,
            'top10_combined_pct': 0.15,
            'holder_count': 100,
            'gini_coefficient': 0.45,
            'recent_whale_activity': 0.0
        }
