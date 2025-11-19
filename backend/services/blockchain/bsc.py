"""
Binance Smart Chain client
"""
from typing import Dict, Any
import logging

from services.blockchain.base_chain import BaseChain
from config.settings import settings
from utils.constants import ERC20_ABI_MINIMAL

logger = logging.getLogger(__name__)


class BSCChain(BaseChain):
    """
    Binance Smart Chain client
    """
    
    def __init__(self):
        super().__init__(
            rpc_url=settings.BSC_RPC,
            chain_name="bsc"
        )
    
    async def get_contract_info(self, address: str) -> Dict[str, Any]:
        """
        Get BEP20 token information
        
        Args:
            address: Token contract address
            
        Returns:
            Contract information dictionary
        """
        info = {
            "address": address,
            "name": None,
            "symbol": None,
            "decimals": None,
            "total_supply": None,
            "is_contract": False
        }
        
        try:
            checksum_address = self.w3.to_checksum_address(address)
            
            # Check if it's a contract
            code = self.w3.eth.get_code(checksum_address)
            is_contract = code and len(code) > 2
            info["is_contract"] = is_contract
            
            if not is_contract:
                logger.warning(f"{address} is not a contract")
                return info
            
            contract = self.w3.eth.contract(
                address=checksum_address,
                abi=ERC20_ABI_MINIMAL
            )
            
            try:
                info["name"] = contract.functions.name().call()
            except Exception:
                pass
            
            try:
                info["symbol"] = contract.functions.symbol().call()
            except Exception:
                pass
            
            try:
                info["decimals"] = contract.functions.decimals().call()
            except Exception:
                pass
            
            try:
                total_supply_wei = contract.functions.totalSupply().call()
                decimals = info["decimals"] or 18
                info["total_supply"] = total_supply_wei / (10 ** decimals)
            except Exception:
                pass
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get contract info for {address}: {str(e)}")
            return info
