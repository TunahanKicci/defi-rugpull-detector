"""
Data formatting utilities
"""
from typing import Any, Dict, Optional
from datetime import datetime
import json


def format_number(value: float, decimals: int = 2) -> str:
    """Format number with decimals"""
    return f"{value:.{decimals}f}"


def format_percentage(value: float) -> str:
    """Format percentage"""
    return f"{value:.2f}%"


def format_currency(value: float, symbol: str = "$") -> str:
    """Format currency value"""
    if value >= 1_000_000:
        return f"{symbol}{value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{symbol}{value/1_000:.2f}K"
    return f"{symbol}{value:.2f}"


def format_token_amount(value: float, decimals: int = 18) -> float:
    """Convert token amount from wei"""
    return value / (10 ** decimals)


def format_timestamp(timestamp: int) -> str:
    """Format Unix timestamp to ISO string"""
    return datetime.fromtimestamp(timestamp).isoformat()


def format_address(address: str, length: int = 10) -> str:
    """Format address for display (shortened)"""
    if len(address) <= length:
        return address
    return f"{address[:6]}...{address[-4:]}"


def safe_json_dumps(data: Any) -> str:
    """Safely serialize data to JSON"""
    try:
        return json.dumps(data, default=str, ensure_ascii=False)
    except Exception:
        return "{}"


def format_risk_level(score: float) -> str:
    """
    Format risk score to level
    
    Args:
        score: Risk score (0-100)
        
    Returns:
        Risk level string
    """
    if score >= 80:
        return "CRITICAL"
    elif score >= 60:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    elif score >= 20:
        return "LOW"
    else:
        return "MINIMAL"


def format_analysis_result(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format analysis result for API response
    
    Args:
        data: Raw analysis data
        
    Returns:
        Formatted response
    """
    return {
        "address": data.get("address"),
        "chain": data.get("chain"),
        "risk_score": round(data.get("risk_score", 0), 2),
        "risk_level": format_risk_level(data.get("risk_score", 0)),
        "analysis": data.get("analysis", {}),
        "timestamp": datetime.utcnow().isoformat(),
        "warnings": data.get("warnings", []),
        "recommendations": data.get("recommendations", [])
    }
