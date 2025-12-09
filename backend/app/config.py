import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./sytescan.db"
    
    # File Storage
    upload_dir: str = "./uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: List[str] = [".jpg", ".jpeg", ".png"]
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    cors_origins: List[str] = ["http://localhost:3000"]
    
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