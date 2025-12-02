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


def analyze_bytecode_characteristics(bytecode: str) -> Dict[str, Any]:
    """
    Analyze basic bytecode characteristics (size, complexity)
    Note: Opcode pattern matching removed due to high false positive rate.
    We rely on function selectors and bytecode size heuristics instead.
    
    Args:
        bytecode: Contract bytecode
        
    Returns:
        Dict with detected patterns and risk score
    """
    if not bytecode or bytecode == "0x":
        return {"patterns": [], "risk": 0}
    
    detected_patterns = []
    risk_score = 0
    
    # Bytecode size analysis - main indicator
    bytecode_size = len(bytecode)
    
    if bytecode_size < 2000:  # Very small - likely minimal/proxy/scam contract
        detected_patterns.append({
            "name": "minimal_bytecode",
            "description": f"Very small bytecode ({bytecode_size} bytes) - minimal implementation",
            "risk": 40
        })
        risk_score += 40
    elif bytecode_size < 4000:  # Small but might be legitimate minimal token
        detected_patterns.append({
            "name": "small_bytecode",
            "description": f"Small bytecode ({bytecode_size} bytes) - limited functionality",
            "risk": 25
        })
        risk_score += 25
    elif bytecode_size > 60000:  # Extremely large - might be obfuscated
        detected_patterns.append({
            "name": "large_bytecode",
            "description": f"Very large bytecode ({bytecode_size//1000}KB) - complex contract",
            "risk": 10
        })
        risk_score += 10
    # Normal size (4000-60000): no penalty
    
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
        
        # Analyze bytecode characteristics (size-based heuristics)
        bytecode_analysis = analyze_bytecode_characteristics(bytecode)
        data["bytecode_patterns"] = bytecode_analysis["patterns"]
        risk_score += bytecode_analysis["risk"]
        
        logger.info(f"Bytecode analysis for {address}: {len(bytecode_analysis['patterns'])} patterns, base risk={bytecode_analysis['risk']}")
        
        # Add warnings for bytecode issues
        for pattern in bytecode_analysis["patterns"]:
            logger.info(f"  Pattern: {pattern['name']} (risk={pattern['risk']})")
            if pattern["risk"] >= 30:
                warnings.append(f"⚠️ {pattern['description']}")
            elif pattern["risk"] >= 10:
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
        
        
        # Check for known function selectors - both risky and positive indicators
        function_selectors = {
            # High-risk functions
            "f9f92be4": ("addToBlackList", 30),  # Blacklist function - very risky
            "e47d6060": ("setMaxTxPercent", 20),  # Can restrict trades
            
            # Medium-risk functions
            "40c10f19": ("mint", 15),  # Mint function (common in tokens)
            "42966c68": ("burn", 5),  # Burn function (less risky)
            "f2fde38b": ("transferOwnership", 10),  # Owner transfer
            
            # Positive security indicators (reduce risk)
            "715018a6": ("renounceOwnership", -25),  # EXCELLENT: owner gave up control
            "dd62ed3e": ("allowance", -3),  # Standard ERC20 function
            "a9059cbb": ("transfer", -3),  # Standard ERC20 function
            "23b872dd": ("transferFrom", -3),  # Standard ERC20 function
            "095ea7b3": ("approve", -3),  # Standard ERC20 function
            "70a08231": ("balanceOf", -3),  # Standard ERC20 function
            "18160ddd": ("totalSupply", -3),  # Standard ERC20 function
        }
        
        bytecode_lower = bytecode.lower()
        risky_functions = []
        positive_functions = []
        selector_risk = 0
        
        for selector, (name, risk) in function_selectors.items():
            if selector in bytecode_lower:
                if risk > 0:  # Risky functions
                    risky_functions.append(name)
                    selector_risk += risk
                elif risk < 0:  # Positive security indicators
                    positive_functions.append(name)
                    selector_risk += risk
        
        logger.info(f"Function analysis: {len(risky_functions)} risky, {len(positive_functions)} positive, selector_risk={selector_risk}")
        
        # Report findings
        if risky_functions:
            warnings.append(f"⚠️ Privileged functions: {', '.join(risky_functions)}")
        
        # Check if this is a standard ERC20 (has basic functions)
        standard_erc20_count = len(positive_functions)
        if standard_erc20_count >= 4:  # Has most standard ERC20 functions
            data["is_standard_erc20"] = True
        else:
            data["is_standard_erc20"] = False
            # Missing standard functions is suspicious for a token
            if standard_erc20_count < 2:
                warnings.append("⚠️ Missing standard ERC20 functions - may not be a real token")
                selector_risk += 15
        
        # Apply selector-based risk (can be negative to reduce score)
        risk_score = max(0, risk_score + selector_risk)
        
        data["risky_functions"] = risky_functions
        data["positive_indicators"] = positive_functions
        
        
        # Bytecode metadata
        import hashlib
        bytecode_hash = hashlib.sha256(bytecode.encode()).hexdigest()
        data["bytecode_hash"] = bytecode_hash[:16]
        data["bytecode_size"] = len(bytecode)
        
        features["risky_function_count"] = len(risky_functions)
        features["positive_indicator_count"] = len(positive_functions)
        features["is_standard_erc20"] = 1 if data.get("is_standard_erc20") else 0
        features["bytecode_size_normalized"] = min(len(bytecode) / 50000, 1.0)
        features["has_mint"] = 1 if "40c10f19" in bytecode_lower else 0
        features["has_blacklist"] = 1 if "f9f92be4" in bytecode_lower else 0
        features["has_renounce_ownership"] = 1 if "715018a6" in bytecode_lower else 0
        
        # Bonus for clean, standard contracts
        if not bytecode_analysis["patterns"] and data.get("is_standard_erc20") and 4000 < len(bytecode) < 40000:
            risk_score = max(0, risk_score - 15)  # Reduce risk for normal-sized standard ERC20
            logger.info(f"Clean standard ERC20 bonus applied: -15 risk")
        
        risk_score = min(risk_score, 100)
        risk_score = max(0, risk_score)  # Ensure non-negative
        
        logger.info(f"Pattern matching complete for {address}: Final Risk={risk_score} (bytecode: {len(bytecode)} bytes, patterns: {len(bytecode_analysis['patterns'])}, standard_erc20: {data.get('is_standard_erc20', False)})")
        
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
