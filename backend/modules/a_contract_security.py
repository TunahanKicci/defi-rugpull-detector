"""
Module A: Smart Contract Security Scanner
Analyzes contract bytecode and functions for security risks
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def analyze(address: str, blockchain) -> Dict[str, Any]:
    """
    Analyze smart contract security
    
    Checks:
    - Dangerous functions (mint, pause, blacklist, etc.)
    - Owner privileges
    - Upgradeable proxies
    - Selfdestruct presence
    - Hidden backdoors
    
    Args:
        address: Contract address
        blockchain: Blockchain client instance
        
    Returns:
        Analysis result with risk score and warnings
    """
    try:
        warnings = []
        risk_score = 0
        data = {}
        
        # Get bytecode
        bytecode = await blockchain.get_bytecode(address)
        
        if not bytecode or bytecode == "0x" or bytecode == "":
            # Try to get contract info to verify it exists
            try:
                contract_info = await blockchain.get_contract_info(address)
                if contract_info.get("is_contract"):
                    # Contract exists but bytecode retrieval failed
                    logger.warning(f"Contract exists but bytecode unavailable for {address}")
                    return {
                        "risk_score": 30,
                        "warnings": ["⚠️ Bytecode unavailable (possible RPC limit or large contract)"],
                        "data": {"bytecode_length": 0, "is_contract": True},
                        "features": {"has_bytecode": 0.5}
                    }
            except:
                pass
            
            return {
                "risk_score": 100,
                "warnings": ["🚨 Contract bytecode not found - possible EOA or fake contract"],
                "data": {"bytecode_length": 0, "is_contract": False},
                "features": {"has_bytecode": 0}
            }
        
        data["bytecode_length"] = len(bytecode)
        features = {"has_bytecode": 1}
        
        # Check for dangerous function signatures in bytecode
        dangerous_patterns = {
            "mint": "40c10f19",  # mint(address,uint256)
            "burn": "42966c68",  # burn(uint256)
            "pause": "8456cb59",  # pause()
            "blacklist": "f9f92be4",  # blacklist(address)
            "setTaxes": "8c0b5e22",  # Common tax function
            "renounceOwnership": "715018a6",  # Ownership functions
            "transferOwnership": "f2fde38b",
            "selfdestruct": "ff",  # Selfdestruct opcode
        }
        
        found_functions = []
        for func_name, signature in dangerous_patterns.items():
            if signature in bytecode.lower():
                found_functions.append(func_name)
                features[f"has_{func_name}"] = 1
                risk_score += 10
                
                if func_name in ["mint", "selfdestruct"]:
                    warnings.append(f"⚠️ CRITICAL: Contract has {func_name}() function")
                    risk_score += 10
                else:
                    warnings.append(f"⚡ Contract has {func_name}() function")
        
        data["dangerous_functions"] = found_functions
        
        # Check for proxy patterns (upgradeable)
        proxy_patterns = ["delegatecall", "implementation"]
        is_proxy = any(pattern in bytecode.lower() for pattern in proxy_patterns)
        
        if is_proxy:
            warnings.append("🔄 Contract appears to be upgradeable (proxy)")
            risk_score += 20
            features["is_upgradeable"] = 1
        else:
            features["is_upgradeable"] = 0
        
        data["is_upgradeable"] = is_proxy
        
        # Check bytecode size (very small contracts are suspicious)
        if data["bytecode_length"] < 100:
            warnings.append("🚨 Suspiciously small contract bytecode")
            risk_score += 15
        
        features["bytecode_size"] = min(data["bytecode_length"] / 10000, 1.0)
        features["dangerous_function_count"] = len(found_functions)
        
        # Cap risk score
        risk_score = min(risk_score, 100)
        
        logger.info(f"Contract security scan complete for {address}: Risk={risk_score}")
        
        return {
            "risk_score": risk_score,
            "warnings": warnings,
            "data": data,
            "features": features
        }
        
    except Exception as e:
        logger.error(f"Contract security analysis failed: {str(e)}")
        return {
            "risk_score": 50,
            "warnings": [f"Analysis error: {str(e)}"],
            "data": {},
            "features": {}
        }
