"""
Global error handling middleware
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import traceback

from config.settings import settings

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Global error handler for uncaught exceptions
    """
    
    async def dispatch(self, request: Request, call_next):
        """Process request with error handling"""
        try:
            response = await call_next(request)
            return response
            
        except Exception as exc:
            # Log the error
            logger.error(
                f"Unhandled exception: {str(exc)}\n"
                f"Path: {request.url.path}\n"
                f"Method: {request.method}\n"
                f"Traceback: {traceback.format_exc()}"
            )
            
            # Return generic error response
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal server error",
                    "message": str(exc) if settings.DEBUG else "An unexpected error occurred",
                    "path": request.url.path
                }
            )
