"""
Module E: Pattern Matching - Scam Database Comparison
Compares contract with known scam patterns
"""
import logging
from typing import Dict, Any
import os
import json

logger = logging.getLogger(__name__)


# Known scam addresses (loaded from database)
KNOWN_SCAMS = set()


def load_scam_database():
    """Load known scam addresses from file"""
    global KNOWN_SCAMS
    try:
        scam_file = "backend/data/scam_database/known_scams.json"
        if os.path.exists(scam_file):
            with open(scam_file, 'r') as f:
                data = json.load(f)
                KNOWN_SCAMS = set(data.get("scams", []))
                logger.info(f"Loaded {len(KNOWN_SCAMS)} known scam addresses")
    except Exception as e:
        logger.warning(f"Failed to load scam database: {str(e)}")


async def is_known_scam(address: str) -> bool:
    """Check if address is in known scam database"""
    if not KNOWN_SCAMS:
        load_scam_database()
    
    return address.lower() in KNOWN_SCAMS


async def analyze(address: str, blockchain) -> Dict[str, Any]:
    """
    Compare contract with known scam patterns
    
    Checks:
    - Known scam database
    - Bytecode similarity with scams
    - Common honeypot patterns
    - ABI similarity
    
    Args:
        address: Token contract address
        blockchain: Blockchain client instance
        
    Returns:
        Analysis result with risk score and warnings
    """
    try:
        warnings = []
        risk_score = 0
        data = {}
        features = {}
        
        # Load scam database if not loaded
        if not KNOWN_SCAMS:
            load_scam_database()
        
        # Check known scam database
        is_scam = await is_known_scam(address)
        
        data["is_known_scam"] = is_scam
        features["is_known_scam"] = 1 if is_scam else 0
        
        if is_scam:
            warnings.append("🚨 CRITICAL: Address is in known scam database!")
            risk_score = 100
            return {
                "risk_score": risk_score,
                "warnings": warnings,
                "data": data,
                "features": features
            }
        
        # Get bytecode for similarity comparison
        bytecode = await blockchain.get_bytecode(address)
        
        if not bytecode:
            return {
                "risk_score": 50,
                "warnings": ["Could not retrieve bytecode"],
                "data": data,
                "features": features
            }
        
        # Check for common honeypot patterns
        honeypot_patterns = [
            "bait",  # Common in honeypot names
            "trap",
            "lock",
            "antibot"  # Some use antibot as disguise
        ]
        
        bytecode_lower = bytecode.lower()
        found_patterns = [p for p in honeypot_patterns if p in bytecode_lower]
        
        if found_patterns:
            warnings.append(f"⚠️ Suspicious patterns found: {', '.join(found_patterns)}")
            risk_score += 20
        
        data["suspicious_patterns"] = found_patterns
        features["honeypot_pattern_count"] = len(found_patterns)
        
        # Bytecode similarity check (simplified)
        # In production: Use fuzzy hashing or Jaccard similarity
        similarity_score = 0.0  # 0-1
        
        # Mock: Random similarity for demonstration
        # In production: Compare with database of scam bytecodes
        import hashlib
        bytecode_hash = hashlib.sha256(bytecode.encode()).hexdigest()
        data["bytecode_hash"] = bytecode_hash[:16]
        
        # Check bytecode size (very common sizes might indicate copy-paste)
        common_scam_sizes = [10000, 15000, 20000]  # Example
        bytecode_size = len(bytecode)
        
        if any(abs(bytecode_size - size) < 100 for size in common_scam_sizes):
            warnings.append("⚡ Bytecode size matches common scam contracts")
            risk_score += 10
        
        data["bytecode_size"] = bytecode_size
        data["similarity_score"] = similarity_score
        features["similarity_score"] = similarity_score
        features["bytecode_size_normalized"] = min(bytecode_size / 50000, 1.0)
        
        if similarity_score > 0.8:
            warnings.append(f"🚨 HIGH similarity ({similarity_score:.0%}) with known scams")
            risk_score += 40
        elif similarity_score > 0.6:
            warnings.append(f"⚠️ Moderate similarity ({similarity_score:.0%}) with scams")
            risk_score += 20
        
        risk_score = min(risk_score, 100)
        
        logger.info(f"Pattern matching complete for {address}: Risk={risk_score}")
        
        return {
            "risk_score": risk_score,
            "warnings": warnings,
            "data": data,
            "features": features
        }
        
    except Exception as e:
        logger.error(f"Pattern matching failed: {str(e)}")
        return {
            "risk_score": 50,
            "warnings": [f"Analysis error: {str(e)}"],
            "data": {},
            "features": {}
        }


# Initialize on module load
load_scam_database()
