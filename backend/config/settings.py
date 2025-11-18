"""
Application Configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "RugPullDetector"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # Blockchain RPC Endpoints
    ETHEREUM_RPC: str = "https://eth.llamarpc.com"
    BSC_RPC: str = "https://bsc-dataseed.binance.org"
    POLYGON_RPC: str = "https://polygon-rpc.com"
    
    # WebSocket RPC
    ETHEREUM_WSS: str = ""
    BSC_WSS: str = ""
    
    # API Keys
    ETHERSCAN_API_KEY: str = ""
    BSCSCAN_API_KEY: str = ""
    POLYGONSCAN_API_KEY: str = ""
    COINGECKO_API_KEY: str = ""
    
    # Database
    MONGODB_URI: str = "mongodb://localhost:27017/rugpulldetector"
    REDIS_URI: str = "redis://localhost:6379/0"
    
    # Cache Configuration
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600
    
    # ML Model Configuration
    MODEL_PATH: str = "backend/data/models"
    SCAM_DATABASE_PATH: str = "backend/data/scam_database"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Monitoring
    ENABLE_WEBSOCKET_MONITORING: bool = True
    WEBSOCKET_RECONNECT_ATTEMPTS: int = 5
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.APP_ENV == "production"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Create global settings instance
settings = Settings()
