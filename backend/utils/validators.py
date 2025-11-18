"""
Input validation utilities
"""
from web3 import Web3
import re
from typing import Optional


def is_valid_address(address: str) -> bool:
    """
    Validate Ethereum address format
    
    Args:
        address: Address to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not address:
        return False
    
    return Web3.is_address(address)


def normalize_address(address: str) -> str:
    """
    Normalize address to checksum format
    
    Args:
        address: Address to normalize
        
    Returns:
        Checksummed address
    """
    return Web3.to_checksum_address(address)


def is_valid_chain(chain: str) -> bool:
    """
    Validate blockchain name
    
    Args:
        chain: Chain name to validate
        
    Returns:
        True if valid, False otherwise
    """
    valid_chains = ["ethereum", "bsc", "polygon"]
    return chain.lower() in valid_chains


def sanitize_string(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input string
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not text:
        return ""
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    
    # Trim to max length
    return text[:max_length].strip()


def validate_contract_address(address: str) -> Optional[str]:
    """
    Validate and normalize contract address
    
    Args:
        address: Contract address to validate
        
    Returns:
        Normalized address or None if invalid
    """
    try:
        if not is_valid_address(address):
            return None
        return normalize_address(address)
    except Exception:
        return None
