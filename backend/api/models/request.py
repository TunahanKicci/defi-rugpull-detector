"""
API Request Models
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional

from utils.validators import is_valid_address, is_valid_chain


class AnalysisRequest(BaseModel):
    """Request model for token analysis"""
    address: str = Field(..., description="Token contract address", min_length=42, max_length=42)
    chain: str = Field("ethereum", description="Blockchain network")
    force_refresh: bool = Field(False, description="Force refresh cached data")
    
    @field_validator('address')
    @classmethod
    def validate_address(cls, v: str) -> str:
        """Validate Ethereum address format"""
        if not is_valid_address(v):
            raise ValueError('Invalid Ethereum address format')
        return v.lower()
    
    @field_validator('chain')
    @classmethod
    def validate_chain(cls, v: str) -> str:
        """Validate chain name"""
        if not is_valid_chain(v):
            raise ValueError(f'Unsupported chain: {v}')
        return v.lower()


class MonitorRequest(BaseModel):
    """Request model for monitoring"""
    address: str = Field(..., description="Token contract address")
    chain: str = Field("ethereum", description="Blockchain network")
    
    @field_validator('address')
    @classmethod
    def validate_address(cls, v: str) -> str:
        if not is_valid_address(v):
            raise ValueError('Invalid Ethereum address format')
        return v.lower()
