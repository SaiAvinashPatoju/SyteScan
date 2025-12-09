from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

# Project schemas
class ProjectCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    requirements: List[str] = Field(..., min_length=1, description="List of required objects")

class ProjectResponse(BaseModel):
    id: str
    name: str
    requirements: List[str]
    created_at: datetime
    
    model_config = {"from_attributes": True}

# Detection schemas
class DetectedObject(BaseModel):
    object_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    bbox_x: Optional[float] = None
    bbox_y: Optional[float] = None
    bbox_width: Optional[float] = None
    bbox_height: Optional[float] = None

class DetectionResult(BaseModel):
    image_path: str
    detected_objects: List[DetectedObject]
    processing_time: float

class UploadResponse(BaseModel):
    uploaded_files: List[str]
    detection_results: List[DetectionResult]

# Progress schemas
class RequirementMatch(BaseModel):
    requirement: str
    detected: bool
    confidence: Optional[float] = None
    count: int = 0

class DetectionSummary(BaseModel):
    total_objects_detected: int
    unique_objects: List[str]
    average_confidence: float

class ProgressResponse(BaseModel):
    project_id: str
    completion_percentage: float = Field(..., ge=0.0, le=100.0)
    requirement_matches: List[RequirementMatch]
    detection_summary: DetectionSummary

# Error schemas
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None