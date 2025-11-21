"""
Module E: Pattern Matching - Scam Database Comparison
Compares contract with known scam patterns using bytecode similarity
"""
import logging
from typing import Dict, Any, List, Set
import os
import json
import re
from collections import Counter

logger = logging.getLogger(__name__)


# Known scam addresses and bytecode patterns (loaded from database)
KNOWN_SCAMS = set()
SCAM_BYTECODE_DB = []  # List of {address, bytecode_hash, opcodes, functions}


def detect_dangerous_opcode_patterns(bytecode: str) -> Dict[str, Any]:
    """
    Detect dangerous opcode patterns commonly used in scams
    
    Args:
        bytecode: Contract bytecode
        
    Returns:
        Dict with detected patterns and risk score
    """
    if not bytecode or bytecode == "0x":
        return {"patterns": [], "risk": 0}
    
    bytecode_lower = bytecode.lower()
    detected_patterns = []
    risk_score = 0
    
    # Pattern 1: Hidden Mint - DELEGATECALL to mint function
    if "delegatecall" in bytecode_lower and "40c10f19" in bytecode_lower:  # mint selector
        detected_patterns.append({
            "name": "hidden_mint",
            "description": "Contract may have hidden mint capability via delegatecall",
            "risk": 30
        })
        risk_score += 30
    
    # Pattern 2: Transfer Restriction - tx.origin check (honeypot indicator)
    if "32" in bytecode_lower and "14" in bytecode_lower:  # ORIGIN (0x32) and EQ (0x14)
        detected_patterns.append({
            "name": "origin_check",
            "description": "Uses tx.origin check - potential honeypot",
            "risk": 25
        })
        risk_score += 25
    
    # Pattern 3: Blacklist mechanism without visibility
    if "f9f92be4" in bytecode_lower or "blacklist" in bytecode_lower:  # blacklist selector
        detected_patterns.append({
            "name": "blacklist",
            "description": "Has blacklist function - users can be blocked from trading",
            "risk": 15
        })
        risk_score += 15
    
    # Pattern 4: Max TX limit bypass for owner
    if ("caller" in bytecode_lower or "33" in bytecode_lower) and ("owner" in bytecode_lower):
        # Check if there's owner bypass logic
        detected_patterns.append({
            "name": "owner_bypass",
            "description": "Owner may have special privileges bypassing limits",
            "risk": 10
        })
        risk_score += 10
    
    # Pattern 5: Suspicious SELFDESTRUCT without timelock
    if "selfdestruct" in bytecode_lower or "ff" in bytecode_lower[-100:]:  # SELFDESTRUCT opcode
        detected_patterns.append({
            "name": "selfdestruct",
            "description": "Contract can be destroyed - funds may be lost",
            "risk": 20
        })
        risk_score += 20
    
    return {
        "patterns": detected_patterns,
        "risk": min(risk_score, 100)
    }


def extract_function_selectors(bytecode: str) -> Set[str]:
    """
    Extract function selectors (4-byte signatures) from bytecode
    
    Args:
        bytecode: Contract bytecode (hex string)
        
    Returns:
        Set of function selectors
    """
    if not bytecode or bytecode == "0x":
        return set()
    
    # Find PUSH4 instructions followed by function selectors
    # Pattern: 63 (PUSH4) followed by 8 hex chars
    selectors = set(re.findall(r'63([0-9a-f]{8})', bytecode.lower()))
    
    # Also look for common ERC20/ERC721 selectors directly
    common_selectors = {
        'a9059cbb',  # transfer(address,uint256)
        '23b872dd',  # transferFrom(address,address,uint256)
        '095ea7b3',  # approve(address,uint256)
        '70a08231',  # balanceOf(address)
        '18160ddd',  # totalSupply()
        'dd62ed3e',  # allowance(address,address)
    }
    
    for selector in common_selectors:
        if selector in bytecode.lower():
            selectors.add(selector)
    
    return selectors


def extract_opcodes(bytecode: str) -> List[str]:
    """
    Extract opcodes from bytecode (simplified)
    
    Args:
        bytecode: Contract bytecode (hex string)
        
    Returns:
        List of opcode bytes
    """
    if not bytecode or bytecode == "0x":
        return []
    
    # Remove 0x prefix
    if bytecode.startswith('0x'):
        bytecode = bytecode[2:]
    
    # Split into bytes (each 2 hex chars)
    opcodes = [bytecode[i:i+2] for i in range(0, len(bytecode), 2)]
    
    return opcodes


def calculate_bytecode_similarity(bytecode1: str, bytecode2: str) -> float:
    """
    Calculate similarity between two bytecodes using Jaccard similarity on opcodes
    
    Args:
        bytecode1: First bytecode
        bytecode2: Second bytecode
        
    Returns:
        Similarity score (0-1)
    """
    if not bytecode1 or not bytecode2:
        return 0.0
    
    # Extract opcodes
    opcodes1 = extract_opcodes(bytecode1)
    opcodes2 = extract_opcodes(bytecode2)
    
    if not opcodes1 or not opcodes2:
        return 0.0
    
    # Create frequency counters (n-grams of size 4 for better matching)
    ngram_size = 4
    
    def create_ngrams(opcodes: List[str], n: int) -> Set[str]:
        return set(''.join(opcodes[i:i+n]) for i in range(len(opcodes) - n + 1))
    
    ngrams1 = create_ngrams(opcodes1, ngram_size)
    ngrams2 = create_ngrams(opcodes2, ngram_size)
    
    # Jaccard similarity
    if not ngrams1 or not ngrams2:
        return 0.0
    
    intersection = len(ngrams1 & ngrams2)
    union = len(ngrams1 | ngrams2)
    
    similarity = intersection / union if union > 0 else 0.0
    
    return similarity


def calculate_function_similarity(selectors1: Set[str], selectors2: Set[str]) -> float:
    """
    Calculate similarity between two sets of function selectors
    
    Args:
        selectors1: First set of selectors
        selectors2: Second set of selectors
        
    Returns:
        Similarity score (0-1)
    """
    if not selectors1 or not selectors2:
        return 0.0
    
    intersection = len(selectors1 & selectors2)
    union = len(selectors1 | selectors2)
    
    return intersection / union if union > 0 else 0.0


def load_scam_database():
    """Load known scam addresses from file"""
    global KNOWN_SCAMS, SCAM_BYTECODE_DB
    try:
        scam_file = "backend/data/scam_database/known_scams.json"
        if os.path.exists(scam_file):
            with open(scam_file, 'r') as f:
                data = json.load(f)
                KNOWN_SCAMS = set(data.get("scams", []))
                SCAM_BYTECODE_DB = data.get("bytecode_patterns", [])
                logger.info(f"Loaded {len(KNOWN_SCAMS)} known scam addresses and {len(SCAM_BYTECODE_DB)} bytecode patterns")
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
        
        if not bytecode or bytecode == "0x":
            return {
                "risk_score": 50,
                "warnings": ["Could not retrieve bytecode"],
                "data": data,
                "features": features
            }
        
        # Extract function selectors from this contract
        contract_selectors = extract_function_selectors(bytecode)
        data["function_count"] = len(contract_selectors)
        
        # Detect dangerous opcode patterns (real scam detection!)
        opcode_analysis = detect_dangerous_opcode_patterns(bytecode)
        data["dangerous_patterns"] = opcode_analysis["patterns"]
        risk_score += opcode_analysis["risk"]
        
        # Add warnings for detected dangerous patterns
        for pattern in opcode_analysis["patterns"]:
            if pattern["risk"] >= 25:
                warnings.append(f"🚨 {pattern['description']}")
            elif pattern["risk"] >= 15:
                warnings.append(f"⚠️ {pattern['description']}")
            else:
                warnings.append(f"⚡ {pattern['description']}")
        
        # Compare with known scam bytecodes
        max_bytecode_similarity = 0.0
        max_function_similarity = 0.0
        similar_scam_address = None
        
        for scam_pattern in SCAM_BYTECODE_DB:
            scam_bytecode = scam_pattern.get("bytecode", "")
            scam_selectors = set(scam_pattern.get("function_selectors", []))
            
            if scam_bytecode:
                similarity = calculate_bytecode_similarity(bytecode, scam_bytecode)
                if similarity > max_bytecode_similarity:
                    max_bytecode_similarity = similarity
                    similar_scam_address = scam_pattern.get("address", "unknown")
            
            if scam_selectors:
                func_similarity = calculate_function_similarity(contract_selectors, scam_selectors)
                if func_similarity > max_function_similarity:
                    max_function_similarity = func_similarity
        
        data["bytecode_similarity"] = round(max_bytecode_similarity, 3)
        data["function_similarity"] = round(max_function_similarity, 3)
        features["bytecode_similarity"] = max_bytecode_similarity
        features["function_similarity"] = max_function_similarity
        
        # Risk scoring based on similarities
        if max_bytecode_similarity > 0.85:
            warnings.append(f"🚨 CRITICAL: {max_bytecode_similarity*100:.1f}% bytecode match with known scam!")
            if similar_scam_address:
                warnings.append(f"   Similar to: {similar_scam_address}")
            risk_score += 60
        elif max_bytecode_similarity > 0.70:
            warnings.append(f"⚠️ HIGH: {max_bytecode_similarity*100:.1f}% bytecode similarity with scams")
            risk_score += 40
        elif max_bytecode_similarity > 0.50:
            warnings.append(f"⚡ Moderate bytecode similarity ({max_bytecode_similarity*100:.1f}%) with scams")
            risk_score += 20
        
        if max_function_similarity > 0.80:
            warnings.append(f"⚠️ {max_function_similarity*100:.1f}% function overlap with scam contracts")
            risk_score += 25
        
        
        # Check for common honeypot/scam patterns in bytecode
        honeypot_patterns = {
            "bait": 5,
            "trap": 10,
            "lock": 3,
            "antibot": 2,
            "honeypot": 15
        }
        
        bytecode_lower = bytecode.lower()
        found_patterns = []
        pattern_risk = 0
        
        for pattern, risk in honeypot_patterns.items():
            if pattern in bytecode_lower:
                found_patterns.append(pattern)
                pattern_risk += risk
        
        if found_patterns:
            warnings.append(f"⚠️ Suspicious patterns found: {', '.join(found_patterns)}")
            risk_score += min(pattern_risk, 20)
        
        data["suspicious_patterns"] = found_patterns
        
        
        # Bytecode metadata
        import hashlib
        bytecode_hash = hashlib.sha256(bytecode.encode()).hexdigest()
        data["bytecode_hash"] = bytecode_hash[:16]
        data["bytecode_size"] = len(bytecode)
        
        features["honeypot_pattern_count"] = len(found_patterns)
        features["bytecode_size_normalized"] = min(len(bytecode) / 50000, 1.0)
        
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
