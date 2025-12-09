import os
from typing import List
from pydantic_settings import BaseSettings

def parse_cors_origins(v: str) -> List[str]:
    """Parse comma-separated CORS origins from environment variable."""
    if isinstance(v, list):
        return v
    if v:
        return [origin.strip() for origin in v.split(",") if origin.strip()]
    return ["http://localhost:3000"]

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./sytescan.db"
    
    # File Storage
    upload_dir: str = "./uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: List[str] = [".jpg", ".jpeg", ".png"]
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    cors_origins_str: str = "http://localhost:3000,https://sytescan.vercel.app,https://sytescan-frontend.vercel.app,https://sytescan.onrender.com,https://sytescan-frontend.onrender.com"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return parse_cors_origins(self.cors_origins_str)
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # YOLOv8 Configuration
    yolo_model: str = "yolov8m.pt"  # Options: yolov8n.pt, yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
    detection_confidence: float = 0.5
    
    # Model performance notes:
    # yolov8n.pt - Fastest, lowest accuracy (~3.2M params)
    # yolov8s.pt - Good balance (~11.2M params) 
    # yolov8m.pt - Better accuracy (~25.9M params)
    # yolov8l.pt - High accuracy (~43.7M params)
    # yolov8x.pt - Highest accuracy, slowest (~68.2M params)
    
    # Performance
    max_workers: int = 4
    request_timeout: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()