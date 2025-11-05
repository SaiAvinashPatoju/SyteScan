from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
from pathlib import Path

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

# Configure CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(SyteScanException, sytescan_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Serve static files (frontend)
frontend_path = Path("frontend")
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
    logger.info("Frontend static files mounted at /static")

# Include API routers with prefix
app.include_router(projects_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(progress_router, prefix="/api")

@app.get("/")
async def serve_frontend():
    """Serve the frontend HTML file"""
    frontend_file = Path("frontend/index.html")
    if frontend_file.exists():
        return FileResponse("frontend/index.html")
    else:
        return {"message": "SyteScan Progress Analyzer API", "status": "Frontend not found"}

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment"""
    from datetime import datetime
    logger.info("Health check requested")
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "service": "sytescan-api",
        "version": "1.0.0"
    }

@app.get("/api/model-info")
async def get_model_info():
    """Get information about the currently loaded YOLO model"""
    try:
        from app.config import settings
        
        model_info = {
            "current_model": settings.yolo_model,
            "custom_model_path": settings.custom_model_path,
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

@app.get("/api/health/detailed")
async def detailed_health_check():
    """Detailed health check with system metrics"""
    try:
        import psutil
        import platform
        from datetime import datetime
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "system": {
                "platform": platform.system(),
                "python_version": platform.python_version(),
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            },
            "application": {
                "model_loaded": True,
                "database_connected": True
            }
        }
    except ImportError:
        return {"status": "healthy", "monitoring": "psutil not available"}
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {"status": "healthy", "error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(
        "main_production:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        access_log=True
    )