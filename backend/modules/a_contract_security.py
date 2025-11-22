"""
Module A: Smart Contract Security Scanner - IMPROVED VERSION
Advanced bytecode analysis with context-aware risk assessment and confidence scoring
"""
import logging
import re
from typing import Dict, Any, List, Tuple, Set
from datetime import datetime

logger = logging.getLogger(__name__)

# Known safe contracts (whitelisted)
WHITELISTED_CONTRACTS = {
    "0xdac17f958d2ee523a2206206994597c13d831ec7": "USDT",  # Tether
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": "USDC",  # USD Coin
    "0x6b175474e89094c44da98b954eedeac495271d0f": "DAI",   # Dai Stablecoin
    "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599": "WBTC",  # Wrapped Bitcoin
    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": "WETH",  # Wrapped Ether
}

# Function signatures with context
FUNCTION_SIGNATURES = {
    # Critical functions (high risk)
    "40c10f19": {"name": "mint", "risk": "critical", "context": "Can create new tokens"},
    "9dc29fac": {"name": "burn", "risk": "medium", "context": "Can destroy tokens"},
    
    # Ownership functions (medium risk - normal for many contracts)
    "715018a6": {"name": "renounceOwnership", "risk": "low", "context": "Can remove owner"},
    "f2fde38b": {"name": "transferOwnership", "risk": "low", "context": "Can transfer ownership"},
    "8da5cb5b": {"name": "owner", "risk": "info", "context": "Has ownership system"},
    
    # Pause functions (medium risk - common in legitimate contracts)
    "8456cb59": {"name": "pause", "risk": "medium", "context": "Can pause transfers"},
    "3f4ba83a": {"name": "unpause", "risk": "medium", "context": "Can unpause transfers"},
    
    # Blacklist functions (high risk)
    "f9f92be4": {"name": "blacklist", "risk": "high", "context": "Can blacklist addresses"},
    "c6d69a30": {"name": "addBlackList", "risk": "high", "context": "Can add to blacklist"},
    
    # Tax/Fee functions (medium-high risk)
    "8c0b5e22": {"name": "setTaxes", "risk": "medium", "context": "Can modify tax rates"},
    "39509351": {"name": "setFees", "risk": "medium", "context": "Can modify fees"},
    
    # Upgrade functions (high risk)
    "3659cfe6": {"name": "upgradeTo", "risk": "high", "context": "Upgradeable proxy"},
    "4f1ef286": {"name": "upgradeToAndCall", "risk": "high", "context": "Upgradeable proxy"},
}

# Selfdestruct patterns (more sophisticated detection)
SELFDESTRUCT_PATTERNS = {
    # SELFDESTRUCT opcode followed by specific patterns
    "critical": [
        r"ff[0-9a-f]{40}",  # SELFDESTRUCT with address
        r"33.*ff",           # CALLER followed by SELFDESTRUCT (sends to caller)
    ],
    "suspicious": [
        r"[0-9a-f]{8}ff00",  # SELFDESTRUCT in function
    ]
}


def is_whitelisted(address: str) -> Tuple[bool, str]:
    """
    Check if contract is whitelisted (known safe contract)
    
    Returns:
        (is_whitelisted, contract_name)
    """
    address_lower = address.lower()
    if address_lower in WHITELISTED_CONTRACTS:
        return True, WHITELISTED_CONTRACTS[address_lower]
    return False, ""


def extract_function_selectors(bytecode: str) -> Set[str]:
    """
    Extract all 4-byte function selectors from bytecode
    
    Args:
        bytecode: Contract bytecode (hex string)
        
    Returns:
        Set of function selectors (4-byte hex strings)
    """
    if not bytecode or bytecode == "0x":
        return set()
    
    selectors = set()
    bytecode_clean = bytecode.lower().replace("0x", "")
    
    # Method 1: Look for PUSH4 (0x63) followed by 4 bytes
    push4_pattern = r'63([0-9a-f]{8})'
    selectors.update(re.findall(push4_pattern, bytecode_clean))
    
    # Method 2: Look for known function selectors directly
    for selector in FUNCTION_SIGNATURES.keys():
        if selector in bytecode_clean:
            selectors.add(selector)
    
    return selectors


def analyze_selfdestruct(bytecode: str) -> Tuple[bool, str, int]:
    """
    Sophisticated SELFDESTRUCT detection with context
    
    Returns:
        (has_selfdestruct, context, risk_score)
    """
    if not bytecode or bytecode == "0x":
        return False, "", 0
    
    bytecode_clean = bytecode.lower().replace("0x", "")
    
    # Check critical patterns first
    for pattern in SELFDESTRUCT_PATTERNS["critical"]:
        if re.search(pattern, bytecode_clean):
            return True, "critical", 30
    
    # Check suspicious patterns
    for pattern in SELFDESTRUCT_PATTERNS["suspicious"]:
        if re.search(pattern, bytecode_clean):
            return True, "suspicious", 15
    
    # Check for standalone FF opcode (common false positive)
    # FF is used in many contexts (e.g., as data, not as opcode)
    ff_count = bytecode_clean.count("ff")
    
    if ff_count > 0:
        # If FF appears many times, it's likely data, not SELFDESTRUCT
        if ff_count > 20:
            return False, "data_pattern", 0
        
        # If FF appears only at the end, it might be padding
        if bytecode_clean.rstrip("f").count("ff") == 0:
            return False, "padding", 0
        
        # Otherwise, it's uncertain
        return True, "uncertain", 5
    
    return False, "", 0


def analyze_proxy_pattern(bytecode: str) -> Tuple[bool, str, int]:
    """
    Detect proxy patterns (upgradeable contracts)
    
    Returns:
        (is_proxy, proxy_type, risk_score)
    """
    if not bytecode or bytecode == "0x":
        return False, "", 0
    
    bytecode_lower = bytecode.lower()
    
    proxy_indicators = {
        "delegatecall": 0,
        "implementation": 0,
        "upgrade": 0,
        "proxy": 0,
    }
    
    for indicator in proxy_indicators.keys():
        if indicator in bytecode_lower:
            proxy_indicators[indicator] = 1
    
    proxy_score = sum(proxy_indicators.values())
    
    if proxy_score >= 3:
        return True, "upgradeable_proxy", 25
    elif proxy_score >= 2:
        return True, "possible_proxy", 15
    elif proxy_score == 1:
        return False, "uses_delegatecall", 5
    
    return False, "", 0


def categorize_functions(selectors: Set[str]) -> Dict[str, List[Dict]]:
    """
    Categorize detected functions by risk level
    
    Returns:
        Dict with categorized functions: {critical: [...], high: [...], medium: [...], low: [...]}
    """
    categorized = {
        "critical": [],
        "high": [],
        "medium": [],
        "low": [],
        "info": []
    }
    
    for selector in selectors:
        if selector in FUNCTION_SIGNATURES:
            func_info = FUNCTION_SIGNATURES[selector]
            risk_level = func_info["risk"]
            categorized[risk_level].append({
                "name": func_info["name"],
                "selector": selector,
                "context": func_info["context"]
            })
    
    return categorized


def calculate_confidence(
    bytecode_length: int,
    selectors_found: int,
    is_whitelisted: bool
) -> Tuple[int, str]:
    """
    Calculate confidence score for the analysis
    
    Returns:
        (confidence_score, quality_label)
    """
    confidence = 100
    
    # No bytecode = low confidence
    if bytecode_length == 0:
        return 0, "no_data"
    
    # Very small bytecode = uncertain
    if bytecode_length < 100:
        confidence = 40
    
    # Whitelisted = high confidence
    if is_whitelisted:
        confidence = 95
    
    # More selectors found = higher confidence in analysis
    if selectors_found < 5:
        confidence -= 10
    
    if confidence >= 80:
        quality = "high"
    elif confidence >= 50:
        quality = "medium"
    else:
        quality = "low"
    
    return confidence, quality


async def analyze(address: str, blockchain) -> Dict[str, Any]:
    """
    IMPROVED Smart Contract Security Analysis
    
    Features:
    - Context-aware function detection
    - Whitelisting for known safe contracts
    - Sophisticated SELFDESTRUCT detection
    - Confidence scoring
    - Risk categorization
    
    Args:
        address: Contract address
        blockchain: Blockchain client instance
        
    Returns:
        Analysis result with risk score, confidence, and detailed warnings
    """
    try:
        warnings = []
        risk_score = 0
        data = {}
        features = {}
        
        # Check if contract is whitelisted
        is_safe, contract_name = is_whitelisted(address)
        if is_safe:
            logger.info(f"✓ Contract is whitelisted: {contract_name}")
            return {
                "risk_score": 0,
                "confidence": 100,
                "warnings": [f"✓ Verified safe contract: {contract_name}"],
                "data": {
                    "is_whitelisted": True,
                    "contract_name": contract_name,
                    "data_quality": "verified"
                },
                "features": {
                    "has_bytecode": 1,
                    "is_whitelisted": 1
                }
            }
        
        # Get bytecode
        try:
            bytecode = await blockchain.get_bytecode(address)
        except TypeError:
            # If not awaitable, call directly
            bytecode = blockchain.get_bytecode(address)
        
        if not bytecode or bytecode == "0x" or bytecode == "":
            logger.warning(f"No bytecode available for {address}")
            return {
                "risk_score": 100,
                "confidence": 0,
                "warnings": ["🚨 Contract bytecode not found - possible EOA or fake contract"],
                "data": {
                    "bytecode_length": 0,
                    "is_contract": False,
                    "data_quality": "no_data"
                },
                "features": {"has_bytecode": 0}
            }
        
        bytecode_length = len(bytecode)
        data["bytecode_length"] = bytecode_length
        features["has_bytecode"] = 1
        
        logger.info(f"Analyzing bytecode ({bytecode_length} bytes) for {address}")
        
        # Extract function selectors
        selectors = extract_function_selectors(bytecode)
        logger.debug(f"Found {len(selectors)} function selectors")
        
        # Categorize functions by risk
        categorized_functions = categorize_functions(selectors)
        
        # Calculate confidence
        confidence, data_quality = calculate_confidence(
            bytecode_length,
            len(selectors),
            False
        )
        
        data["data_quality"] = data_quality
        data["confidence_score"] = confidence
        
        # Risk Assessment
        
        # 1. CRITICAL FUNCTIONS
        if categorized_functions["critical"]:
            for func in categorized_functions["critical"]:
                warnings.append(f"🚨 CRITICAL: {func['name']}() - {func['context']}")
                risk_score += 25
            data["critical_functions"] = [f["name"] for f in categorized_functions["critical"]]
        
        # 2. HIGH RISK FUNCTIONS
        if categorized_functions["high"]:
            for func in categorized_functions["high"]:
                warnings.append(f"⚠️ HIGH RISK: {func['name']}() - {func['context']}")
                risk_score += 15
            data["high_risk_functions"] = [f["name"] for f in categorized_functions["high"]]
        
        # 3. MEDIUM RISK FUNCTIONS (more lenient)
        if categorized_functions["medium"]:
            # Only warn if there are many medium risk functions
            if len(categorized_functions["medium"]) > 2:
                for func in categorized_functions["medium"][:3]:  # Show max 3
                    warnings.append(f"⚡ {func['name']}() - {func['context']}")
                risk_score += 5 * len(categorized_functions["medium"])
            data["medium_risk_functions"] = [f["name"] for f in categorized_functions["medium"]]
        
        # 4. LOW RISK FUNCTIONS (informational only)
        if categorized_functions["low"]:
            # Don't add warnings, just log
            logger.debug(f"Low risk functions: {[f['name'] for f in categorized_functions['low']]}")
            data["low_risk_functions"] = [f["name"] for f in categorized_functions["low"]]
        
        # 5. SELFDESTRUCT DETECTION (improved)
        has_selfdestruct, sd_context, sd_risk = analyze_selfdestruct(bytecode)
        
        if has_selfdestruct:
            if sd_context == "critical":
                warnings.append("🚨 CRITICAL: Contract has SELFDESTRUCT capability")
                risk_score += sd_risk
            elif sd_context == "suspicious":
                warnings.append("⚠️ Suspicious SELFDESTRUCT pattern detected")
                risk_score += sd_risk
            elif sd_context == "uncertain":
                warnings.append("ℹ️ Possible SELFDESTRUCT opcode (uncertain)")
                risk_score += sd_risk
            # "data_pattern" and "padding" don't trigger warnings
        
        data["has_selfdestruct"] = has_selfdestruct
        data["selfdestruct_context"] = sd_context
        features["has_selfdestruct"] = 1 if has_selfdestruct and sd_context in ["critical", "suspicious"] else 0
        
        # 6. PROXY PATTERN DETECTION
        is_proxy, proxy_type, proxy_risk = analyze_proxy_pattern(bytecode)
        
        if is_proxy:
            if proxy_type == "upgradeable_proxy":
                warnings.append("🔄 Contract is upgradeable (proxy pattern)")
                risk_score += proxy_risk
            elif proxy_type == "possible_proxy":
                warnings.append("⚡ Contract may be upgradeable")
                risk_score += proxy_risk
            elif proxy_type == "uses_delegatecall":
                warnings.append("ℹ️ Contract uses delegatecall")
                risk_score += proxy_risk
        
        data["is_proxy"] = is_proxy
        data["proxy_type"] = proxy_type
        features["is_upgradeable"] = 1 if is_proxy else 0
        
        # 7. BYTECODE SIZE CHECK
        if bytecode_length < 100:
            warnings.append("🚨 Suspiciously small contract bytecode")
            risk_score += 20
        elif bytecode_length > 100000:
            warnings.append("ℹ️ Very large contract (>100KB)")
            # Large doesn't mean risky
        
        features["bytecode_size"] = min(bytecode_length / 100000, 1.0)
        
        # 8. FUNCTION COUNT
        total_dangerous = len(categorized_functions["critical"]) + len(categorized_functions["high"])
        features["dangerous_function_count"] = total_dangerous
        
        # Summary data
        data["total_functions_analyzed"] = len(selectors)
        data["dangerous_function_count"] = total_dangerous
        
        # Cap risk score
        risk_score = min(risk_score, 100)
        
        logger.info(
            f"✅ Contract security scan complete for {address}: "
            f"Risk={risk_score}, Confidence={confidence}%, "
            f"Functions={total_dangerous} dangerous"
        )
        
        return {
            "risk_score": risk_score,
            "confidence": confidence,
            "warnings": warnings,
            "data": data,
            "features": features
        }
        
    except Exception as e:
        logger.error(f"Contract security analysis failed: {str(e)}", exc_info=True)
        return {
            "risk_score": 50,
            "confidence": 0,
            "warnings": [f"⚠️ Analysis error: {str(e)}"],
            "data": {
                "error": str(e),
                "data_quality": "failed"
            },
            "features": {}
        }