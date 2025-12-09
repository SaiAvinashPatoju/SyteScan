from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class DetectedObjectResponse(BaseModel):
    name: str
    confidence: float
    bbox: List[float] = Field(..., description="Bounding box [x, y, width, height]")

class DetectionResult(BaseModel):
    image_path: str
    filename: str
    detected_objects: List[DetectedObjectResponse]
    processing_time: float
    created_at: datetime

class UploadResponse(BaseModel):
    project_id: str
    uploaded_files: List[str]
    detection_results: List[DetectionResult]
    total_objects_detected: int
    processing_summary: dict

class UploadError(BaseModel):
    error: str
    details: Optional[str] = None
    failed_files: Optional[List[str]] = None