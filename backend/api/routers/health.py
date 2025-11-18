"""
Health check endpoint
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    
    Returns service status and basic info
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "RugPull Detector API",
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check():
    """
    Readiness check for load balancers
    
    Returns whether the service is ready to accept requests
    """
    # TODO: Add checks for database connections, ML models loaded, etc.
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat()
    }
