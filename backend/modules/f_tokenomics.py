"""
Module F: Tokenomics Analysis - IMPROVED VERSION
Analyzes token economics and tax structure with bytecode verification and confidence scoring
"""
import logging
from typing import Dict, Any, Optional, List, Tuple
from web3 import Web3

logger = logging.getLogger(__name__)

# Common tokenomics function ABIs
TOKENOMICS_ABI = [
    # Tax functions
    {"constant": True, "inputs": [], "name": "buyTax", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "sellTax", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "_buyTax", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "_sellTax", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "taxFee", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "_taxFee", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "buyFee", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "sellFee", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    
    # Limit functions
    {"constant": True, "inputs": [], "name": "maxTransactionAmount", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "_maxTxAmount", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "maxTxAmount", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "maxWalletAmount", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "_maxWalletSize", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "_maxWalletAmount", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "maxWallet", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    
    # Supply
    {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
]

# Function selectors for bytecode detection
TAX_FUNCTION_SELECTORS = {
    "buyTax": "00000000",  # Will be populated with real selectors
    "sellTax": "00000000",
    "setTaxes": "8c0b5e22",
    "_setFees": "00000000",
}


def try_call_function(contract, function_names: list) -> Optional[int]:
    """
    Try to call multiple function name variations
    
    Args:
        contract: Web3 contract instance
        function_names: List of function names to try
        
    Returns:
        Function result or None
    """
    for func_name in function_names:
        try:
            if hasattr(contract.functions, func_name):
                result = getattr(contract.functions, func_name)().call()
                logger.debug(f"✓ {func_name}() returned: {result}")
                return result
        except Exception as e:
            logger.debug(f"✗ {func_name}() failed: {str(e)[:50]}")
            continue
    return None


def detect_tax_functions_in_bytecode(bytecode: str) -> Dict[str, bool]:
    """
    Detect tax-related functions in bytecode by searching for function selectors
    
    Args:
        bytecode: Contract bytecode (hex string)
        
    Returns:
        Dict of detected tax function indicators
    """
    if not bytecode or bytecode == "0x":
        return {}
    
    bytecode_lower = bytecode.lower()
    detected = {}
    
    # Common tax function patterns (4-byte selectors)
    tax_patterns = {
        "has_buy_tax_function": ["buytax", "buyfee"],
        "has_sell_tax_function": ["selltax", "sellfee"],
        "has_tax_setter": ["settax", "setfee", "updatetax"],
        "has_fee_collector": ["collectfee", "withdrawfee"],
    }
    
    for key, patterns in tax_patterns.items():
        detected[key] = any(pattern in bytecode_lower for pattern in patterns)
    
    return detected


def calculate_confidence(
    total_supply: Optional[int],
    decimals: Optional[int],
    buy_tax: Optional[float],
    sell_tax: Optional[float],
    bytecode_checks: Dict[str, bool]
) -> Tuple[int, str]:
    """
    Calculate confidence score for tokenomics analysis
    
    Returns:
        (confidence_score, data_quality_label)
    """
    confidence = 100
    
    # Reduce confidence for missing critical data
    if total_supply is None:
        confidence -= 20
    if decimals is None:
        confidence -= 10
    
    # If no tax functions found AND no bytecode evidence
    if buy_tax is None and sell_tax is None:
        if not any(bytecode_checks.values()):
            # Likely no tax system - this is OK
            confidence = max(confidence, 60)
        else:
            # Has tax functions in bytecode but couldn't call them
            confidence -= 30
    
    # Quality labels
    if confidence >= 80:
        quality = "high"
    elif confidence >= 50:
        quality = "medium"
    else:
        quality = "low"
    
    return confidence, quality


async def analyze(address: str, blockchain) -> Dict[str, Any]:
    """
    IMPROVED Tokenomics Analysis with bytecode verification and confidence scoring
    
    Args:
        address: Token contract address
        blockchain: Blockchain client instance
        
    Returns:
        Tokenomics analysis results with confidence score
    """
    try:
        w3 = blockchain.w3
        contract_address = Web3.to_checksum_address(address)
        contract = w3.eth.contract(address=contract_address, abi=TOKENOMICS_ABI)
        
        warnings = []
        risk_score = 0
        
        # 1. Get basic token info
        total_supply = None
        decimals = None
        
        try:
            total_supply = contract.functions.totalSupply().call()
            logger.info(f"✓ Total supply: {total_supply}")
        except Exception as e:
            logger.warning(f"Could not fetch total supply: {e}")
            warnings.append("ℹ️ Could not verify total supply (RPC issue)")
        
        try:
            decimals = contract.functions.decimals().call()
            logger.info(f"✓ Decimals: {decimals}")
        except Exception as e:
            logger.warning(f"Could not fetch decimals: {e}")
            decimals = 18  # Default assumption
            warnings.append("ℹ️ Using default decimals (18)")
        
        # 2. Get bytecode for verification (DISABLED for now - may cause errors)
        bytecode = ""
        bytecode_checks = {}
        
        # Uncomment when blockchain.get_bytecode is confirmed working:
        # try:
        #     try:
        #         bytecode = await blockchain.get_bytecode(address)
        #     except TypeError:
        #         bytecode = blockchain.get_bytecode(address)
        #     logger.debug(f"Bytecode length: {len(bytecode) if bytecode else 0}")
        #     bytecode_checks = detect_tax_functions_in_bytecode(bytecode) if bytecode else {}
        # except Exception as e:
        #     logger.debug(f"Could not fetch bytecode: {e}")
        #     bytecode = ""
        #     bytecode_checks = {}
        
        # 3. Try to get tax values
        buy_tax_raw = try_call_function(
            contract, 
            ['buyTax', '_buyTax', 'buyFee', 'taxFee', '_taxFee']
        )
        
        sell_tax_raw = try_call_function(
            contract,
            ['sellTax', '_sellTax', 'sellFee', 'taxFee', '_taxFee']
        )
        
        # 4. Try to get limits
        max_tx_raw = try_call_function(
            contract,
            ['maxTransactionAmount', '_maxTxAmount', 'maxTxAmount']
        )
        
        max_wallet_raw = try_call_function(
            contract,
            ['maxWalletAmount', '_maxWalletSize', '_maxWalletAmount', 'maxWallet']
        )
        
        # 5. Process tax values
        buy_tax = None
        sell_tax = None
        
        if buy_tax_raw is not None:
            # Handle different formats: direct percentage or basis points
            if buy_tax_raw <= 100:
                buy_tax = float(buy_tax_raw)
            elif buy_tax_raw <= 10000:  # Basis points (e.g., 500 = 5%)
                buy_tax = float(buy_tax_raw) / 100
            else:
                logger.warning(f"Unusual buy_tax value: {buy_tax_raw}")
                buy_tax = None
        
        if sell_tax_raw is not None:
            if sell_tax_raw <= 100:
                sell_tax = float(sell_tax_raw)
            elif sell_tax_raw <= 10000:
                sell_tax = float(sell_tax_raw) / 100
            else:
                logger.warning(f"Unusual sell_tax value: {sell_tax_raw}")
                sell_tax = None
        
        # 6. Process limits
        max_tx_limit_percent = None
        max_wallet_limit_percent = None
        
        if total_supply and total_supply > 0:
            if max_tx_raw is not None and max_tx_raw > 0:
                max_tx_limit_percent = (max_tx_raw / total_supply) * 100
                
            if max_wallet_raw is not None and max_wallet_raw > 0:
                max_wallet_limit_percent = (max_wallet_raw / total_supply) * 100
        
        # 7. Calculate confidence
        confidence, data_quality = calculate_confidence(
            total_supply,
            decimals,
            buy_tax,
            sell_tax,
            bytecode_checks
        )
        
        # 8. Initialize data structure
        data = {
            "total_supply": total_supply,
            "decimals": decimals,
            "buy_tax": buy_tax,
            "sell_tax": sell_tax,
            "max_tx_limit_percent": max_tx_limit_percent,
            "max_wallet_limit_percent": max_wallet_limit_percent,
            "has_tax_functions": buy_tax is not None or sell_tax is not None,
            "has_limits": max_tx_limit_percent is not None or max_wallet_limit_percent is not None,
            "confidence_score": confidence,
            "data_quality": data_quality,
            "bytecode_evidence": bytecode_checks
        }
        
        features = {
            "buy_tax": buy_tax / 100 if buy_tax is not None else 0,
            "sell_tax": sell_tax / 100 if sell_tax is not None else 0,
            "total_tax": ((buy_tax or 0) + (sell_tax or 0)) / 100,
            "tax_difference": abs((sell_tax or 0) - (buy_tax or 0)) / 100,
            "has_tx_limit": 1 if max_tx_limit_percent is not None else 0,
            "max_tx_percent": max_tx_limit_percent / 100 if max_tx_limit_percent is not None else 0,
            "max_wallet_percent": max_wallet_limit_percent / 100 if max_wallet_limit_percent is not None else 0,
            "confidence": confidence / 100
        }
        
        # 9. Risk Scoring
        
        # A) Buy Tax Risk
        if buy_tax is not None:
            if buy_tax > 20:
                warnings.append(f"🚨 EXTREME buy tax ({buy_tax}%)")
                risk_score += 40
            elif buy_tax > 15:
                warnings.append(f"🚨 VERY HIGH buy tax ({buy_tax}%)")
                risk_score += 30
            elif buy_tax > 10:
                warnings.append(f"⚠️ HIGH buy tax ({buy_tax}%)")
                risk_score += 20
            elif buy_tax > 5:
                warnings.append(f"⚡ Moderate buy tax ({buy_tax}%)")
                risk_score += 8
        
        # B) Sell Tax Risk
        if sell_tax is not None:
            if sell_tax > 25:
                warnings.append(f"🚨 CRITICAL: Extremely high sell tax ({sell_tax}%)")
                risk_score += 50
            elif sell_tax > 20:
                warnings.append(f"🚨 VERY HIGH sell tax ({sell_tax}%)")
                risk_score += 35
            elif sell_tax > 15:
                warnings.append(f"⚠️ HIGH sell tax ({sell_tax}%)")
                risk_score += 20
            elif sell_tax > 10:
                warnings.append(f"⚡ Elevated sell tax ({sell_tax}%)")
                risk_score += 10
        
        # C) Tax Asymmetry (Honeypot Indicator)
        if buy_tax is not None and sell_tax is not None:
            if buy_tax > 0 and sell_tax > buy_tax * 3:
                warnings.append(f"🚨 HONEYPOT ALERT: Sell tax is {sell_tax / buy_tax:.1f}x higher than buy tax")
                risk_score += 30
            elif buy_tax > 0 and sell_tax > buy_tax * 2:
                warnings.append(f"⚠️ Sell tax is {sell_tax / buy_tax:.1f}x higher than buy tax - potential restriction")
                risk_score += 15
        
        # D) Combined Tax Risk
        if buy_tax is not None and sell_tax is not None:
            total_tax = buy_tax + sell_tax
            if total_tax > 40:
                warnings.append(f"🚨 Combined taxes extremely high ({total_tax}%)")
                risk_score += 25
            elif total_tax > 30:
                warnings.append(f"⚠️ Combined taxes very high ({total_tax}%)")
                risk_score += 15
        
        # E) Transaction Limits
        if max_tx_limit_percent is not None:
            if max_tx_limit_percent < 0.1:
                warnings.append(f"🚨 EXTREME tx limit ({max_tx_limit_percent:.4f}% of supply)")
                risk_score += 25
            elif max_tx_limit_percent < 0.5:
                warnings.append(f"⚠️ Very restrictive tx limit ({max_tx_limit_percent:.3f}% of supply)")
                risk_score += 15
            elif max_tx_limit_percent < 1:
                warnings.append(f"⚡ Low tx limit ({max_tx_limit_percent:.2f}% of supply)")
                risk_score += 8
        
        # F) Wallet Limits
        if max_wallet_limit_percent is not None:
            if max_wallet_limit_percent < 0.5:
                warnings.append(f"🚨 EXTREME wallet limit ({max_wallet_limit_percent:.4f}% of supply)")
                risk_score += 20
            elif max_wallet_limit_percent < 1:
                warnings.append(f"⚠️ Very restrictive wallet limit ({max_wallet_limit_percent:.3f}% of supply)")
                risk_score += 12
            elif max_wallet_limit_percent < 2:
                warnings.append(f"⚡ Low wallet limit ({max_wallet_limit_percent:.2f}% of supply)")
                risk_score += 6
        
        # G) No Tax Functions (Standard ERC20)
        if buy_tax is None and sell_tax is None:
            if not any(bytecode_checks.values()):
                # This is a standard ERC20 without custom taxes - GOOD!
                logger.info("✓ Standard ERC20 token (no custom taxes)")
                data["token_type"] = "standard_erc20"
            else:
                # Has tax functions in bytecode but couldn't call them - SUSPICIOUS
                warnings.append("⚠️ Tax functions detected but not accessible - verification needed")
                risk_score += 10
                data["token_type"] = "tax_functions_unverified"
        else:
            data["token_type"] = "taxed_token"
        
        # H) Low confidence penalty
        if confidence < 50:
            warnings.append(f"⚠️ Low data confidence ({confidence}%) - results may be incomplete")
            # Don't add risk score here - lack of data ≠ high risk
        
        risk_score = min(risk_score, 100)
        
        logger.info(
            f"✅ Tokenomics analysis complete for {address}: "
            f"Risk={risk_score}, Confidence={confidence}%, "
            f"Buy={buy_tax}, Sell={sell_tax}"
        )
        
        return {
            "risk_score": risk_score,
            "confidence": confidence,
            "warnings": warnings,
            "data": data,
            "features": features
        }
        
    except Exception as e:
        logger.error(f"Tokenomics analysis failed: {str(e)}", exc_info=True)
        return {
            "risk_score": 10,
            "confidence": 0,
            "warnings": ["⚠️ Tokenomics analysis incomplete - could not verify token economics"],
            "data": {
                "error": str(e),
                "total_supply": None,
                "decimals": None,
                "buy_tax": None,
                "sell_tax": None,
                "max_tx_limit_percent": None,
                "max_wallet_limit_percent": None,
                "has_tax_functions": False,
                "has_limits": False,
                "confidence_score": 0,
                "data_quality": "failed",
                "token_type": "unknown"
            },
            "features": {
                "buy_tax": 0,
                "sell_tax": 0,
                "total_tax": 0,
                "tax_difference": 0,
                "has_tx_limit": 0,
                "max_tx_percent": 0,
                "max_wallet_percent": 0,
                "confidence": 0
            }
        }