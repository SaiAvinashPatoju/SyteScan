"""
Error handling middleware for structured error responses
"""
import logging
from typing import Dict, Any
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions import SyteScanException

logger = logging.getLogger(__name__)


class ErrorResponse:
    """Structured error response format"""
    
    def __init__(
        self, 
        error: str, 
        message: str, 
        status_code: int, 
        details: Dict[str, Any] = None,
        request_id: str = None
    ):
        self.error = error
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.request_id = request_id
    
    def to_dict(self) -> Dict[str, Any]:
        response = {
            "error": self.error,
            "message": self.message,
            "status_code": self.status_code,
        }
        
        if self.details:
            response["details"] = self.details
            
        if self.request_id:
            response["request_id"] = self.request_id
            
        return response


async def sytescan_exception_handler(request: Request, exc: SyteScanException) -> JSONResponse:
    """Handle custom SyteScan exceptions"""
    logger.error(f"SyteScan exception: {exc.message}", extra={
        "status_code": exc.status_code,
        "details": exc.details,
        "path": request.url.path
    })
    
    error_response = ErrorResponse(
        error=exc.__class__.__name__,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
        request_id=getattr(request.state, 'request_id', None)
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.to_dict()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors"""
    logger.warning(f"Validation error: {exc.errors()}", extra={
        "path": request.url.path,
        "errors": exc.errors()
    })
    
    error_response = ErrorResponse(
        error="ValidationError",
        message="Request validation failed",
        status_code=422,
        details={"validation_errors": exc.errors()},
        request_id=getattr(request.state, 'request_id', None)
    )
    
    return JSONResponse(
        status_code=422,
        content=error_response.to_dict()
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions"""
    logger.warning(f"HTTP exception: {exc.detail}", extra={
        "status_code": exc.status_code,
        "path": request.url.path
    })
    
    error_response = ErrorResponse(
        error="HTTPException",
        message=exc.detail,
        status_code=exc.status_code,
        request_id=getattr(request.state, 'request_id', None)
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.to_dict()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", extra={
        "path": request.url.path,
        "exception_type": exc.__class__.__name__
    }, exc_info=True)
    
    error_response = ErrorResponse(
        error="InternalServerError",
        message="An unexpected error occurred",
        status_code=500,
        request_id=getattr(request.state, 'request_id', None)
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.to_dict()
    )