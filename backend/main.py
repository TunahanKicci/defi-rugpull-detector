"""
DeFi Rug Pull Detector - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from api.routers import analysis, monitoring, history, health
from api.middleware.cors import setup_cors
from api.middleware.rate_limiter import RateLimitMiddleware
from api.middleware.error_handler import ErrorHandlerMiddleware
from config.settings import settings
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 Starting RugPull Detector API...")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    
    # Startup logic
    # Load ML models, initialize connections, etc.
    
    yield
    
    # Shutdown logic
    logger.info("🛑 Shutting down RugPull Detector API...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="DeFi Rug Pull Detection API - Analyze token contracts for potential scams",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Setup CORS
setup_cors(app)

# Add custom middleware
app.add_middleware(RateLimitMiddleware)
app.add_middleware(ErrorHandlerMiddleware)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(analysis.router, prefix="/api", tags=["Analysis"])
app.include_router(monitoring.router, prefix="/api", tags=["Monitoring"])
app.include_router(history.router, prefix="/api", tags=["History"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🛡️ DeFi Rug Pull Detector API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
