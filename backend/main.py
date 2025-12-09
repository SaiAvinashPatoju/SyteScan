from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from contextlib import asynccontextmanager
from app.api.projects import router as projects_router
from app.api.upload import router as upload_router
from app.api.progress import router as progress_router
from app.database.connection import create_tables
from app.exceptions import SyteScanException
from app.middleware.error_handler import (
    sytescan_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from app.middleware.logging import LoggingMiddleware
from app.config import settings
import uvicorn
import logging
import os

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up SyteScan API...")
    create_tables()
    logger.info("Database tables created/verified")
    yield
    # Shutdown
    logger.info("Shutting down SyteScan API...")

app = FastAPI(
    title="SyteScan Progress Analyzer API",
    description="AI-powered construction progress tracking API",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(LoggingMiddleware)

# Configure CORS - Log allowed origins for debugging
cors_origins = settings.cors_origins
logger.info(f"CORS allowed origins: {cors_origins}")

# Check if wildcard is requested (for debugging)
if "*" in cors_origins:
    logger.warning("CORS wildcard '*' enabled - use only for debugging!")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # Must be False with wildcard
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add exception handlers
app.add_exception_handler(SyteScanException, sytescan_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(projects_router)
app.include_router(upload_router)
app.include_router(progress_router)

@app.get("/")
async def root():
    return {"message": "SyteScan Progress Analyzer API"}

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    from datetime import datetime
    logger.info("Health check requested")
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/model-info")
async def get_model_info():
    """Get information about the currently loaded YOLO model"""
    try:
        from app.config import settings
        
        model_info = {
            "current_model": settings.yolo_model,
            "detection_confidence": settings.detection_confidence,
            "available_models": {
                "yolov8n.pt": {"size": "Nano", "params": "~3.2M", "speed": "Fastest", "accuracy": "Lowest"},
                "yolov8s.pt": {"size": "Small", "params": "~11.2M", "speed": "Fast", "accuracy": "Good"},
                "yolov8m.pt": {"size": "Medium", "params": "~25.9M", "speed": "Medium", "accuracy": "Better"},
                "yolov8l.pt": {"size": "Large", "params": "~43.7M", "speed": "Slow", "accuracy": "High"},
                "yolov8x.pt": {"size": "Extra Large", "params": "~68.2M", "speed": "Slowest", "accuracy": "Highest"}
            }
        }
        
        return model_info
        
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        return {"error": "Failed to get model information"}

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with system metrics"""
    try:
        from app.monitoring.metrics import monitor
        return monitor.get_health_status()
    except ImportError:
        return {"status": "healthy", "monitoring": "disabled"}

@app.get("/metrics")
async def get_metrics():
    """Application metrics endpoint"""
    try:
        from app.monitoring.metrics import monitor
        return {
            "system": monitor.get_system_metrics(),
            "application": monitor.get_application_metrics()
        }
    except ImportError:
        return {"status": "metrics disabled"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)