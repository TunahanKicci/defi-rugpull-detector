"""
API Response Models
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class ModuleResult(BaseModel):
    """Individual module analysis result"""
    module_name: str = Field(..., description="Module identifier")
    risk_score: float = Field(..., ge=0, le=100, description="Module risk score")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    data: Dict[str, Any] = Field(default_factory=dict, description="Module-specific data")


class ContractInfo(BaseModel):
    """Basic contract information"""
    address: str
    name: Optional[str] = None
    symbol: Optional[str] = None
    decimals: Optional[int] = None
    total_supply: Optional[float] = None
    chain: str


class AnalysisResponse(BaseModel):
    """Complete analysis response"""
    address: str = Field(..., description="Token contract address")
    chain: str = Field(..., description="Blockchain network")
    contract_info: ContractInfo = Field(..., description="Basic contract information")
    risk_score: float = Field(..., ge=0, le=100, description="Overall risk score (0-100)")
    risk_level: str = Field(..., description="Risk level (MINIMAL, LOW, MEDIUM, HIGH, CRITICAL)")
    
    # Module results
    modules: Dict[str, ModuleResult] = Field(..., description="Individual module results")
    
    # Honeypot Simulation (Special - separate from modules)
    honeypot_simulation: Optional[Dict[str, Any]] = Field(None, description="Dynamic honeypot simulation results")
    
    # Aggregated insights
    warnings: List[str] = Field(default_factory=list, description="All warnings")
    red_flags: List[str] = Field(default_factory=list, description="Critical issues")
    recommendations: List[str] = Field(default_factory=list, description="User recommendations")
    
    # ML Explainability
    feature_importance: Optional[Dict[str, float]] = Field(None, description="Feature importance scores")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    analysis_duration_ms: Optional[float] = Field(None, description="Analysis duration in milliseconds")
    cached: bool = Field(False, description="Whether result was cached")
    
    class Config:
        json_schema_extra = {
            "example": {
                "address": "0x1234567890123456789012345678901234567890",
                "chain": "ethereum",
                "contract_info": {
                    "address": "0x1234567890123456789012345678901234567890",
                    "name": "Example Token",
                    "symbol": "EXT",
                    "decimals": 18,
                    "total_supply": 1000000,
                    "chain": "ethereum"
                },
                "risk_score": 75.5,
                "risk_level": "HIGH",
                "modules": {},
                "warnings": ["No liquidity lock detected"],
                "red_flags": ["Owner can mint unlimited tokens"],
                "recommendations": ["Avoid investing until liquidity is locked"],
                "timestamp": "2025-01-01T00:00:00",
                "cached": False
            }
        }


class QuickCheckResponse(BaseModel):
    """Quick check response (lightweight)"""
    address: str
    chain: str
    risk_score: float = Field(..., ge=0, le=100)
    risk_level: str
    is_known_scam: bool = Field(False, description="Whether token is in known scam database")
    cached: bool = Field(True, description="Quick checks always use cache")


class MonitoringStatus(BaseModel):
    """Monitoring status response"""
    address: str
    chain: str
    monitoring: bool = Field(..., description="Whether monitoring is active")
    alerts: List[Dict[str, Any]] = Field(default_factory=list, description="Recent alerts")
    last_update: Optional[datetime] = Field(None, description="Last update timestamp")
