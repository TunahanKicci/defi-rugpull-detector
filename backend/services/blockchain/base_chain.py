
"""
Base Blockchain Client - Abstract class for blockchain interactions
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from web3 import Web3
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


class BaseChain(ABC):
    """
    Abstract base class for blockchain clients
    """
    
    def __init__(self, rpc_url: str, chain_name: str):
        self.chain_name = chain_name
        self.rpc_url = rpc_url
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        if not self.w3.is_connected():
            logger.warning(f"Failed to connect to {chain_name} RPC: {rpc_url}")
    
    @abstractmethod
    async def get_contract_info(self, address: str) -> Dict[str, Any]:
        """Get basic contract information"""
        pass
    
    async def get_bytecode(self, address: str) -> str:
        """
        Get contract bytecode
        
        Args:
            address: Contract address
            
        Returns:
            Contract bytecode as hex string
        """
        try:
            checksum_address = self.w3.to_checksum_address(address)
            bytecode = self.w3.eth.get_code(checksum_address)
            
            # Log for debugging
            if bytecode and len(bytecode) > 2:
                logger.info(f"Retrieved bytecode for {address}: {len(bytecode)} bytes")
            else:
                logger.warning(f"No bytecode found for {address}")
            
            return bytecode.hex() if bytecode else "0x"
        except Exception as e:
            logger.error(f"Failed to get bytecode for {address}: {str(e)}")
            return "0x"
    
    async def get_balance(self, address: str) -> float:
        """
        Get native token balance
        
        Args:
            address: Wallet address
            
        Returns:
            Balance in native token (ETH, BNB, etc.)
        """
        try:
            checksum_address = self.w3.to_checksum_address(address)
            balance_wei = self.w3.eth.get_balance(checksum_address)
            return self.w3.from_wei(balance_wei, 'ether')
        except Exception as e:
            logger.error(f"Failed to get balance for {address}: {str(e)}")
            return 0.0
    
    async def get_transaction_count(self, address: str) -> int:
        """
        Get transaction count (nonce)
        
        Args:
            address: Wallet address
            
        Returns:
            Transaction count
        """
        try:
            checksum_address = self.w3.to_checksum_address(address)
            return self.w3.eth.get_transaction_count(checksum_address)
        except Exception as e:
            logger.error(f"Failed to get tx count for {address}: {str(e)}")
            return 0
    
    async def call_contract_function(
        self,
        contract_address: str,
        function_name: str,
        abi: List[Dict],
        *args
    ) -> Any:
        """
        Call a read-only contract function
        
        Args:
            contract_address: Contract address
            function_name: Function name to call
            abi: Contract ABI
            *args: Function arguments
            
        Returns:
            Function result
        """
        try:
            checksum_address = self.w3.to_checksum_address(contract_address)
            contract = self.w3.eth.contract(address=checksum_address, abi=abi)
            func = getattr(contract.functions, function_name)
            return func(*args).call()
        except Exception as e:
            logger.error(f"Failed to call {function_name} on {contract_address}: {str(e)}")
            raise
    
    async def get_logs(
        self,
        contract_address: str,
        event_signature: str,
        from_block: int,
        to_block: int = None
    ) -> List[Dict]:
        """
        Get event logs from contract
        
        Args:
            contract_address: Contract address
            event_signature: Event signature hash
            from_block: Starting block
            to_block: Ending block (None for latest)
            
        Returns:
            List of event logs
        """
        try:
            checksum_address = self.w3.to_checksum_address(contract_address)
            
            if to_block is None:
                to_block = self.w3.eth.block_number
            
            logs = self.w3.eth.get_logs({
                'address': checksum_address,
                'topics': [event_signature],
                'fromBlock': from_block,
                'toBlock': to_block
            })
            
            return [dict(log) for log in logs]
        except Exception as e:
            logger.error(f"Failed to get logs for {contract_address}: {str(e)}")
            return []
    
    async def get_block_number(self) -> int:
        """Get current block number"""
        try:
            return self.w3.eth.block_number
        except Exception as e:
            logger.error(f"Failed to get block number: {str(e)}")
            return 0
    
    def is_contract(self, address: str) -> bool:
        """
        Check if address is a contract
        
        Args:
            address: Address to check
            
        Returns:
            True if contract, False if EOA
        """
        try:
            checksum_address = self.w3.to_checksum_address(address)
            code = self.w3.eth.get_code(checksum_address)
            return len(code) > 0
        except Exception:
            return False
