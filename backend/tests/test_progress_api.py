import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status
from main import app
from app.schemas.project import ProgressResponse, RequirementMatch, DetectionSummary

client = TestClient(app)

class TestProgressAPI:
    
    @patch('app.api.progress.ProgressService')
    @patch('app.api.progress.get_db')
    def test_get_project_progress_success(self, mock_get_db, mock_progress_service_class):
        """Test successful progress retrieval"""
        # Setup
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        mock_progress_service = Mock()
        mock_progress_service_class.return_value = mock_progress_service
        
        # Mock progress response
        mock_progress_response = ProgressResponse(
            project_id="test-project-id",
            completion_percentage=75.0,
            requirement_matches=[
                RequirementMatch(requirement="chair", detected=True, confidence=0.9, count=2),
                RequirementMatch(requirement="table", detected=True, confidence=0.8, count=1),
                RequirementMatch(requirement="lamp", detected=False, confidence=None, count=0)
            ],
            detection_summary=DetectionSummary(
                total_objects_detected=3,
                unique_objects=["chair", "table"],
                average_confidence=0.85
            )
        )
        
        mock_progress_service.calculate_project_progress = AsyncMock(return_value=mock_progress_response)
        
        # Execute
        response = client.get("/api/projects/test-project-id/progress")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["project_id"] == "test-project-id"
        assert data["completion_percentage"] == 75.0
        assert len(data["requirement_matches"]) == 3
        assert data["detection_summary"]["total_objects_detected"] == 3
        
        # Verify service was called correctly
        mock_progress_service_class.assert_called_once()
        mock_progress_service.calculate_project_progress.assert_called_once_with("test-project-id")
    
    @patch('app.api.progress.ProgressService')
    @patch('app.api.progress.get_db')
    def test_get_project_progress_not_found(self, mock_get_db, mock_progress_service_class):
        """Test progress retrieval for non-existent project"""
        # Setup
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        mock_progress_service = Mock()
        mock_progress_service_class.return_value = mock_progress_service
        mock_progress_service.calculate_project_progress = AsyncMock(return_value=None)
        
        # Execute
        response = client.get("/api/projects/nonexistent-id/progress")
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    @patch('app.api.progress.ProgressService')
    @patch('app.api.progress.get_db')
    def test_get_project_progress_internal_error(self, mock_get_db, mock_progress_service_class):
        """Test progress retrieval with internal server error"""
        # Setup
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        mock_progress_service = Mock()
        mock_progress_service_class.return_value = mock_progress_service
        mock_progress_service.calculate_project_progress = AsyncMock(side_effect=Exception("Database error"))
        
        # Execute
        response = client.get("/api/projects/test-project-id/progress")
        
        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        
        data = response.json()
        assert "internal server error" in data["detail"].lower()
    
    def test_get_project_progress_invalid_project_id(self):
        """Test progress retrieval with invalid project ID format"""
        # This test verifies that the endpoint handles various project ID formats
        # The actual validation depends on your project ID format requirements
        
        response = client.get("/api/projects//progress")  # Empty project ID
        # The response will depend on FastAPI's path parameter handling
        # This might return 404 or 422 depending on the route configuration
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    @patch('app.api.progress.ProgressService')
    @patch('app.api.progress.get_db')
    def test_get_project_progress_zero_completion(self, mock_get_db, mock_progress_service_class):
        """Test progress retrieval with zero completion percentage"""
        # Setup
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        mock_progress_service = Mock()
        mock_progress_service_class.return_value = mock_progress_service
        
        # Mock progress response with zero completion
        mock_progress_response = ProgressResponse(
            project_id="test-project-id",
            completion_percentage=0.0,
            requirement_matches=[
                RequirementMatch(requirement="chair", detected=False, confidence=None, count=0),
                RequirementMatch(requirement="table", detected=False, confidence=None, count=0)
            ],
            detection_summary=DetectionSummary(
                total_objects_detected=0,
                unique_objects=[],
                average_confidence=0.0
            )
        )
        
        mock_progress_service.calculate_project_progress = AsyncMock(return_value=mock_progress_response)
        
        # Execute
        response = client.get("/api/projects/test-project-id/progress")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["completion_percentage"] == 0.0
        assert all(not match["detected"] for match in data["requirement_matches"])
        assert data["detection_summary"]["total_objects_detected"] == 0
    
    @patch('app.api.progress.ProgressService')
    @patch('app.api.progress.get_db')
    def test_get_project_progress_full_completion(self, mock_get_db, mock_progress_service_class):
        """Test progress retrieval with full completion percentage"""
        # Setup
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        mock_progress_service = Mock()
        mock_progress_service_class.return_value = mock_progress_service
        
        # Mock progress response with full completion
        mock_progress_response = ProgressResponse(
            project_id="test-project-id",
            completion_percentage=100.0,
            requirement_matches=[
                RequirementMatch(requirement="chair", detected=True, confidence=0.95, count=2),
                RequirementMatch(requirement="table", detected=True, confidence=0.88, count=1)
            ],
            detection_summary=DetectionSummary(
                total_objects_detected=3,
                unique_objects=["chair", "table"],
                average_confidence=0.91
            )
        )
        
        mock_progress_service.calculate_project_progress = AsyncMock(return_value=mock_progress_response)
        
        # Execute
        response = client.get("/api/projects/test-project-id/progress")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["completion_percentage"] == 100.0
        assert all(match["detected"] for match in data["requirement_matches"])
        assert data["detection_summary"]["total_objects_detected"] == 3