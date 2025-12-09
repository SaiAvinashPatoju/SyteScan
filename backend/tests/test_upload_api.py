import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from main import app
from app.schemas.upload import UploadResponse, DetectionResult, DetectedObjectResponse
from datetime import datetime
import io
from PIL import Image

client = TestClient(app)

class TestUploadAPI:
    
    @pytest.fixture
    def sample_image_file(self):
        """Create a sample image file for testing"""
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return ("test_image.jpg", img_bytes, "image/jpeg")
    
    @pytest.fixture
    def mock_upload_response(self):
        """Create a mock upload response"""
        return UploadResponse(
            project_id="test-project-id",
            uploaded_files=["/path/to/image.jpg"],
            detection_results=[
                DetectionResult(
                    image_path="/path/to/image.jpg",
                    filename="test_image.jpg",
                    detected_objects=[
                        DetectedObjectResponse(
                            name="chair",
                            confidence=0.8,
                            bbox=[10, 20, 30, 40]
                        )
                    ],
                    processing_time=1.5,
                    created_at=datetime.now()
                )
            ],
            total_objects_detected=1,
            processing_summary={
                "total_files_uploaded": 1,
                "total_files_processed": 1,
                "total_objects_detected": 1,
                "average_processing_time": 1.5
            }
        )
    
    @patch('app.api.upload.UploadService')
    def test_upload_images_success(self, mock_upload_service, sample_image_file, mock_upload_response):
        """Test successful image upload"""
        # Mock the upload service
        mock_service_instance = Mock()
        mock_service_instance.process_uploads = AsyncMock(return_value=mock_upload_response)
        mock_upload_service.return_value = mock_service_instance
        
        # Make request
        response = client.post(
            "/api/projects/test-project-id/upload",
            files={"files": sample_image_file}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == "test-project-id"
        assert data["total_objects_detected"] == 1
        assert len(data["detection_results"]) == 1
    
    @patch('app.api.upload.UploadService')
    def test_upload_images_multiple_files(self, mock_upload_service, mock_upload_response):
        """Test uploading multiple images"""
        # Create multiple image files
        files = []
        for i in range(3):
            img = Image.new('RGB', (100, 100), color='red')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            files.append(("files", (f"test_image_{i}.jpg", img_bytes, "image/jpeg")))
        
        # Mock the upload service
        mock_service_instance = Mock()
        mock_upload_response.processing_summary["total_files_uploaded"] = 3
        mock_service_instance.process_uploads = AsyncMock(return_value=mock_upload_response)
        mock_upload_service.return_value = mock_service_instance
        
        # Make request
        response = client.post(
            "/api/projects/test-project-id/upload",
            files=files
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["processing_summary"]["total_files_uploaded"] == 3
    
    @patch('app.api.upload.UploadService')
    def test_upload_images_project_not_found(self, mock_upload_service, sample_image_file):
        """Test upload with non-existent project"""
        from fastapi import HTTPException
        
        # Mock the upload service to raise HTTPException
        mock_service_instance = Mock()
        mock_service_instance.process_uploads = AsyncMock(
            side_effect=HTTPException(status_code=404, detail="Project not found")
        )
        mock_upload_service.return_value = mock_service_instance
        
        # Make request
        response = client.post(
            "/api/projects/nonexistent-project/upload",
            files={"files": sample_image_file}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    @patch('app.api.upload.UploadService')
    def test_upload_images_validation_error(self, mock_upload_service, sample_image_file):
        """Test upload with validation error"""
        from fastapi import HTTPException
        
        # Mock the upload service to raise validation error
        mock_service_instance = Mock()
        mock_service_instance.process_uploads = AsyncMock(
            side_effect=HTTPException(status_code=400, detail="Invalid file format")
        )
        mock_upload_service.return_value = mock_service_instance
        
        # Make request
        response = client.post(
            "/api/projects/test-project-id/upload",
            files={"files": sample_image_file}
        )
        
        assert response.status_code == 400
        assert "Invalid file format" in response.json()["detail"]
    
    @patch('app.api.upload.UploadService')
    def test_upload_images_internal_error(self, mock_upload_service, sample_image_file):
        """Test upload with internal server error"""
        # Mock the upload service to raise unexpected error
        mock_service_instance = Mock()
        mock_service_instance.process_uploads = AsyncMock(
            side_effect=Exception("Unexpected error")
        )
        mock_upload_service.return_value = mock_service_instance
        
        # Make request
        response = client.post(
            "/api/projects/test-project-id/upload",
            files={"files": sample_image_file}
        )
        
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]
    
    def test_upload_images_no_files(self):
        """Test upload with no files"""
        response = client.post("/api/projects/test-project-id/upload")
        
        assert response.status_code == 422  # Validation error
    
    @patch('app.api.upload.UploadService')
    def test_get_project_images_success(self, mock_upload_service):
        """Test getting project images"""
        # Mock the upload service
        mock_service_instance = Mock()
        mock_service_instance.get_project_images.return_value = [
            "/path/to/image1.jpg",
            "/path/to/image2.png"
        ]
        mock_upload_service.return_value = mock_service_instance
        
        # Make request
        response = client.get("/api/projects/test-project-id/images")
        
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == "test-project-id"
        assert data["count"] == 2
        assert len(data["images"]) == 2
    
    @patch('app.api.upload.UploadService')
    def test_get_project_images_error(self, mock_upload_service):
        """Test getting project images with error"""
        # Mock the upload service to raise error
        mock_service_instance = Mock()
        mock_service_instance.get_project_images.side_effect = Exception("Access denied")
        mock_upload_service.return_value = mock_service_instance
        
        # Make request
        response = client.get("/api/projects/test-project-id/images")
        
        assert response.status_code == 500
        assert "Failed to retrieve" in response.json()["detail"]
    
    @patch('app.database.connection.get_db')
    def test_get_project_detections_success(self, mock_get_db):
        """Test getting project detections"""
        # Mock database session and queries
        mock_db = Mock()
        mock_get_db.return_value.__enter__.return_value = mock_db
        
        # Mock project
        mock_project = Mock()
        mock_project.id = "test-project-id"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_project
        
        # Mock detections
        mock_detection = Mock()
        mock_detection.image_path = "/path/to/image.jpg"
        mock_detection.object_name = "chair"
        mock_detection.confidence = 0.8
        mock_detection.bbox_x = 10
        mock_detection.bbox_y = 20
        mock_detection.bbox_width = 30
        mock_detection.bbox_height = 40
        
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_detection]
        
        # Make request
        response = client.get("/api/projects/test-project-id/detections")
        
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == "test-project-id"
        assert data["total_detections"] == 1
        assert data["images_processed"] == 1
    
    @patch('app.database.connection.get_db')
    def test_get_project_detections_project_not_found(self, mock_get_db):
        """Test getting detections for non-existent project"""
        # Mock database session
        mock_db = Mock()
        mock_get_db.return_value.__enter__.return_value = mock_db
        
        # Mock project not found
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Make request
        response = client.get("/api/projects/nonexistent-project/detections")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]