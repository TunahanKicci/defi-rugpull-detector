"""
Cache Manager for storing analysis results
"""
import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Simple in-memory cache manager
    
    For production, use Redis
    """
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = 3600  # 1 hour default TTL
    
    def _make_key(self, address: str, chain: str) -> str:
        """Create cache key"""
        return f"{chain}:{address.lower()}"
    
    async def get_analysis(self, address: str, chain: str) -> Optional[Dict[str, Any]]:
        """
        Get cached analysis result
        
        Args:
            address: Token contract address
            chain: Blockchain network
            
        Returns:
            Cached result or None
        """
        key = self._make_key(address, chain)
        
        if key not in self.cache:
            return None
        
        cached_data = self.cache[key]
        
        # Check if expired
        cached_time = datetime.fromisoformat(cached_data.get("cached_at", ""))
        if datetime.utcnow() - cached_time > timedelta(seconds=self.ttl):
            del self.cache[key]
            logger.debug(f"Cache expired for {key}")
            return None
        
        logger.info(f"Cache hit for {key}")
        return cached_data.get("data")
    
    async def set_analysis(self, address: str, chain: str, data: Dict[str, Any]) -> bool:
        """
        Cache analysis result
        
        Args:
            address: Token contract address
            chain: Blockchain network
            data: Analysis result to cache
            
        Returns:
            True if successful
        """
        key = self._make_key(address, chain)
        
        self.cache[key] = {
            "data": data,
            "cached_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Cached analysis for {key}")
        return True
    
    async def invalidate(self, address: str, chain: str) -> bool:
        """
        Invalidate cache for an address
        
        Args:
            address: Token contract address
            chain: Blockchain network
            
        Returns:
            True if invalidated
        """
        key = self._make_key(address, chain)
        
        if key in self.cache:
            del self.cache[key]
            logger.info(f"Cache invalidated for {key}")
            return True
        
        return False
    
    async def clear_all(self) -> int:
        """
        Clear all cached data
        
        Returns:
            Number of entries cleared
        """
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"Cleared {count} cache entries")
        return count
