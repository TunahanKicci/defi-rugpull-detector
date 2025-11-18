"""
Rate limiting middleware
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiter
    
    For production, use Redis-based rate limiting
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.requests = defaultdict(list)
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = datetime.now()
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/ready"]:
            return await call_next(request)
        
        # Get client identifier (IP address)
        client_ip = request.client.host
        
        # Cleanup old entries periodically
        if (datetime.now() - self.last_cleanup).seconds > self.cleanup_interval:
            self._cleanup()
        
        # Check rate limit
        if not self._check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Record request
        self.requests[client_ip].append(datetime.now())
        
        response = await call_next(request)
        return response
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """
        Check if client has exceeded rate limit
        
        Args:
            client_ip: Client IP address
            
        Returns:
            True if within limit, False otherwise
        """
        now = datetime.now()
        
        # Remove requests older than 1 minute
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if (now - req_time).seconds < 60
        ]
        
        # Check per-minute limit
        if len(self.requests[client_ip]) >= settings.RATE_LIMIT_PER_MINUTE:
            return False
        
        return True
    
    def _cleanup(self):
        """Remove old request records"""
        now = datetime.now()
        cutoff = now - timedelta(minutes=5)
        
        for client_ip in list(self.requests.keys()):
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if req_time > cutoff
            ]
            
            # Remove empty entries
            if not self.requests[client_ip]:
                del self.requests[client_ip]
        
        self.last_cleanup = now
        logger.debug("Rate limiter cleanup completed")
