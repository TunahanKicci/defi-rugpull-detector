
"""
Module F: Tokenomics Analysis
Analyzes token economics and tax structure using real blockchain data
"""
import logging
from typing import Dict, Any, Optional
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
    
    # Limit functions
    {"constant": True, "inputs": [], "name": "maxTransactionAmount", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "_maxTxAmount", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "maxWalletAmount", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "_maxWalletSize", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "_maxWalletAmount", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    
    # Supply
    {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
]


def try_call_function(contract, function_names: list, timeout: int = 3) -> Optional[int]:
    """
    Try to call multiple function name variations with timeout
    
    Args:
        contract: Web3 contract instance
        function_names: List of function names to try
        timeout: Timeout in seconds per call
        
    Returns:
        Function result or None
    """
    for func_name in function_names:
        try:
            if hasattr(contract.functions, func_name):
                # Call with timeout to avoid hanging
                result = getattr(contract.functions, func_name)().call(timeout=timeout)
                return result
        except Exception as e:
            # Silently continue to next function
            continue
    return None


async def analyze(address: str, blockchain) -> Dict[str, Any]:
    """
    Analyze token economics using real blockchain data
    Gracefully handles RPC errors and rate limits
    
    Args:
        address: Token contract address
        blockchain: Blockchain client instance
        
    Returns:
        Tokenomics analysis results
    """
    try:
        w3 = blockchain.w3
        contract_address = Web3.to_checksum_address(address)
        contract = w3.eth.contract(address=contract_address, abi=TOKENOMICS_ABI)
        
        # Get total supply - quick call with short timeout
        total_supply = None
        try:
            total_supply = contract.functions.totalSupply().call(timeout=3)
        except Exception as e:
            # Don't log as error, just skip
            pass
        
        # Get decimals - quick call
        decimals = None
        try:
            decimals = contract.functions.decimals().call(timeout=3)
        except Exception as e:
            pass
        
        # Try to get buy tax - with timeout
        buy_tax_raw = try_call_function(contract, ['buyTax', '_buyTax', 'taxFee', '_taxFee'], timeout=2)
        
        # Try to get sell tax - with timeout
        sell_tax_raw = try_call_function(contract, ['sellTax', '_sellTax', 'taxFee', '_taxFee'], timeout=2)
        
        # Try to get max transaction amount - with timeout
        max_tx_raw = try_call_function(contract, [
            'maxTransactionAmount', 
            '_maxTxAmount',
            'maxTxAmount'
        ], timeout=2)
        
        # Try to get max wallet amount - with timeout
        max_wallet_raw = try_call_function(contract, [
            'maxWalletAmount',
            '_maxWalletSize',
            '_maxWalletAmount',
            'maxWallet'
        ], timeout=2)
        
        # Calculate percentages and limits
        buy_tax = None
        sell_tax = None
        max_tx_limit_percent = None
        max_wallet_limit_percent = None
        
        # Tax values are usually stored as percentage (e.g., 5 = 5%)
        # or as basis points (e.g., 500 = 5%)
        if buy_tax_raw is not None:
            buy_tax = buy_tax_raw if buy_tax_raw <= 100 else buy_tax_raw / 100
            
        if sell_tax_raw is not None:
            sell_tax = sell_tax_raw if sell_tax_raw <= 100 else sell_tax_raw / 100
        
        # Calculate limits as percentage of total supply
        if total_supply and total_supply > 0:
            if max_tx_raw is not None and max_tx_raw > 0:
                max_tx_limit_percent = (max_tx_raw / total_supply) * 100
                
            if max_wallet_raw is not None and max_wallet_raw > 0:
                max_wallet_limit_percent = (max_wallet_raw / total_supply) * 100
        
        # Initialize result
        warnings = []
        risk_score = 0
        data = {
            "total_supply": total_supply,
            "decimals": decimals,
            "buy_tax": buy_tax,
            "sell_tax": sell_tax,
            "max_tx_limit_percent": max_tx_limit_percent,
            "max_wallet_limit_percent": max_wallet_limit_percent,
            "has_tax_functions": buy_tax is not None or sell_tax is not None,
            "has_limits": max_tx_limit_percent is not None or max_wallet_limit_percent is not None
        }
        
        features = {
            "buy_tax": buy_tax / 100 if buy_tax is not None else 0,
            "sell_tax": sell_tax / 100 if sell_tax is not None else 0,
            "total_tax": ((buy_tax or 0) + (sell_tax or 0)) / 100,
            "tax_difference": abs((sell_tax or 0) - (buy_tax or 0)) / 100,
            "has_tx_limit": 1 if max_tx_limit_percent is not None else 0,
            "max_tx_percent": max_tx_limit_percent / 100 if max_tx_limit_percent is not None else 0,
            "max_wallet_percent": max_wallet_limit_percent / 100 if max_wallet_limit_percent is not None else 0
        }
        
        # Analyze buy tax
        if buy_tax is not None:
            if buy_tax > 15:
                warnings.append(f"🚨 VERY HIGH buy tax ({buy_tax}%)")
                risk_score += 30
            elif buy_tax > 10:
                warnings.append(f"⚠️ HIGH buy tax ({buy_tax}%)")
                risk_score += 15
            elif buy_tax > 5:
                warnings.append(f"⚡ Moderate buy tax ({buy_tax}%)")
                risk_score += 5
        
        # Analyze sell tax
        if sell_tax is not None:
            if sell_tax > 20:
                warnings.append(f"🚨 CRITICAL: Extremely high sell tax ({sell_tax}%)")
                risk_score += 40
            elif sell_tax > 15:
                warnings.append(f"🚨 VERY HIGH sell tax ({sell_tax}%)")
                risk_score += 25
            elif sell_tax > 10:
                warnings.append(f"⚠️ HIGH sell tax ({sell_tax}%)")
                risk_score += 10
        
        # Check tax asymmetry (honeypot indicator)
        if buy_tax is not None and sell_tax is not None and buy_tax > 0:
            if sell_tax > buy_tax * 2:
                warnings.append(f"⚠️ Sell tax is {sell_tax / buy_tax:.1f}x higher than buy tax - potential honeypot")
                risk_score += 15
        
        # Check transaction limits
        if max_tx_limit_percent is not None:
            if max_tx_limit_percent < 0.5:
                warnings.append(f"⚠️ Very restrictive tx limit ({max_tx_limit_percent:.4f}% of supply)")
                risk_score += 15
            elif max_tx_limit_percent < 1:
                warnings.append(f"⚡ Low tx limit ({max_tx_limit_percent:.2f}% of supply)")
                risk_score += 5
        
        # Check wallet limits
        if max_wallet_limit_percent is not None:
            if max_wallet_limit_percent < 1:
                warnings.append(f"⚠️ Very restrictive wallet limit ({max_wallet_limit_percent:.4f}% of supply)")
                risk_score += 10
            elif max_wallet_limit_percent < 2:
                warnings.append(f"⚡ Low wallet limit ({max_wallet_limit_percent:.2f}% of supply)")
                risk_score += 5
        
        # Total tax check
        if buy_tax is not None and sell_tax is not None:
            total_tax = buy_tax + sell_tax
            if total_tax > 30:
                warnings.append(f"🚨 Combined taxes very high ({total_tax}%)")
                risk_score += 20
        
        risk_score = min(risk_score, 100)
        
        logger.info(f"Tokenomics analysis complete for {address}: Risk={risk_score}, "
                   f"buy_tax={buy_tax}, sell_tax={sell_tax}")
        
        return {
            "risk_score": risk_score,
            "warnings": warnings,
            "data": data,
            "features": features
        }
        
    except Exception as e:
        logger.error(f"Tokenomics analysis failed: {str(e)}")
        return {
            "risk_score": 0,
            "warnings": [f"Analysis error: {str(e)}"],
            "data": {
                "error": str(e),
                "total_supply": None,
                "decimals": None,
                "buy_tax": None,
                "sell_tax": None,
                "max_tx_limit_percent": None,
                "max_wallet_limit_percent": None,
                "has_tax_functions": False,
                "has_limits": False
            },
            "features": {
                "buy_tax": 0,
                "sell_tax": 0,
                "total_tax": 0,
                "tax_difference": 0,
                "has_tx_limit": 0,
                "max_tx_percent": 0,
                "max_wallet_percent": 0
            }
        }
