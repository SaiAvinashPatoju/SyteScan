import pytest
from pydantic import ValidationError
from app.schemas.project import (
    ProjectCreateRequest,
    ProjectResponse,
    DetectedObject,
    DetectionResult,
    ProgressResponse,
    RequirementMatch,
    DetectionSummary
)
from datetime import datetime

def test_project_create_request_valid():
    """Test valid project creation request"""
    data = {
        "name": "Test Project",
        "requirements": ["chair", "table", "lamp"]
    }
    request = ProjectCreateRequest(**data)
    assert request.name == "Test Project"
    assert len(request.requirements) == 3
    assert "chair" in request.requirements

def test_project_create_request_invalid_empty_name():
    """Test project creation with empty name"""
    data = {
        "name": "",
        "requirements": ["chair"]
    }
    with pytest.raises(ValidationError):
        ProjectCreateRequest(**data)

def test_project_create_request_invalid_empty_requirements():
    """Test project creation with empty requirements"""
    data = {
        "name": "Test Project",
        "requirements": []
    }
    with pytest.raises(ValidationError):
        ProjectCreateRequest(**data)

def test_detected_object_valid():
    """Test valid detected object"""
    data = {
        "object_name": "chair",
        "confidence": 0.85,
        "bbox_x": 100.0,
        "bbox_y": 200.0,
        "bbox_width": 50.0,
        "bbox_height": 75.0
    }
    obj = DetectedObject(**data)
    assert obj.object_name == "chair"
    assert obj.confidence == 0.85

def test_detected_object_invalid_confidence():
    """Test detected object with invalid confidence"""
    data = {
        "object_name": "chair",
        "confidence": 1.5  # Invalid: > 1.0
    }
    with pytest.raises(ValidationError):
        DetectedObject(**data)

def test_detection_result_valid():
    """Test valid detection result"""
    detected_objects = [
        DetectedObject(object_name="chair", confidence=0.85),
        DetectedObject(object_name="table", confidence=0.92)
    ]
    
    data = {
        "image_path": "/uploads/test.jpg",
        "detected_objects": detected_objects,
        "processing_time": 2.5
    }
    result = DetectionResult(**data)
    assert result.image_path == "/uploads/test.jpg"
    assert len(result.detected_objects) == 2
    assert result.processing_time == 2.5

def test_requirement_match_valid():
    """Test valid requirement match"""
    data = {
        "requirement": "chair",
        "detected": True,
        "confidence": 0.85,
        "count": 2
    }
    match = RequirementMatch(**data)
    assert match.requirement == "chair"
    assert match.detected is True
    assert match.count == 2

def test_detection_summary_valid():
    """Test valid detection summary"""
    data = {
        "total_objects_detected": 5,
        "unique_objects": ["chair", "table", "lamp"],
        "average_confidence": 0.87
    }
    summary = DetectionSummary(**data)
    assert summary.total_objects_detected == 5
    assert len(summary.unique_objects) == 3
    assert summary.average_confidence == 0.87

def test_progress_response_valid():
    """Test valid progress response"""
    requirement_matches = [
        RequirementMatch(requirement="chair", detected=True, confidence=0.85, count=2),
        RequirementMatch(requirement="table", detected=False, count=0)
    ]
    
    detection_summary = DetectionSummary(
        total_objects_detected=2,
        unique_objects=["chair"],
        average_confidence=0.85
    )
    
    data = {
        "project_id": "test-project-id",
        "completion_percentage": 50.0,
        "requirement_matches": requirement_matches,
        "detection_summary": detection_summary
    }
    
    response = ProgressResponse(**data)
    assert response.project_id == "test-project-id"
    assert response.completion_percentage == 50.0
    assert len(response.requirement_matches) == 2

def test_progress_response_invalid_percentage():
    """Test progress response with invalid percentage"""
    data = {
        "project_id": "test-project-id",
        "completion_percentage": 150.0,  # Invalid: > 100.0
        "requirement_matches": [],
        "detection_summary": DetectionSummary(
            total_objects_detected=0,
            unique_objects=[],
            average_confidence=0.0
        )
    }
    with pytest.raises(ValidationError):
        ProgressResponse(**data)