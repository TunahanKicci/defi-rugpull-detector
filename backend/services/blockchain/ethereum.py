"""
Ethereum blockchain client
"""
from typing import Dict, Any
import logging

from services.blockchain.base_chain import BaseChain
from config.settings import settings
from utils.constants import ERC20_ABI_MINIMAL

logger = logging.getLogger(__name__)


class EthereumChain(BaseChain):
    """
    Ethereum mainnet client
    """
    
    def __init__(self):
        super().__init__(
            rpc_url=settings.ETHEREUM_RPC,
            chain_name="ethereum"
        )
    
    async def get_contract_info(self, address: str) -> Dict[str, Any]:
        """
        Get ERC20 token information
        
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
            "total_supply": None
        }
        
        try:
            checksum_address = self.w3.to_checksum_address(address)
            
            # Check if it's a contract
            if not self.is_contract(address):
                logger.warning(f"{address} is not a contract")
                return info
            
            # Create contract instance with minimal ABI
            contract = self.w3.eth.contract(
                address=checksum_address,
                abi=ERC20_ABI_MINIMAL
            )
            
            # Try to get token info (may fail if not ERC20)
            try:
                info["name"] = contract.functions.name().call()
            except Exception:
                logger.debug(f"Failed to get name for {address}")
            
            try:
                info["symbol"] = contract.functions.symbol().call()
            except Exception:
                logger.debug(f"Failed to get symbol for {address}")
            
            try:
                info["decimals"] = contract.functions.decimals().call()
            except Exception:
                logger.debug(f"Failed to get decimals for {address}")
            
            try:
                total_supply_wei = contract.functions.totalSupply().call()
                decimals = info["decimals"] or 18
                info["total_supply"] = total_supply_wei / (10 ** decimals)
            except Exception:
                logger.debug(f"Failed to get total supply for {address}")
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get contract info for {address}: {str(e)}")
            return info
