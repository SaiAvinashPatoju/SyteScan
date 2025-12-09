import pytest
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from PIL import Image
import io
from app.services.upload_service import UploadService
from app.services.detection_service import DetectedObject
from app.models.project import Project, Requirement, Detection

class TestUploadService:
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def mock_project(self):
        """Create a mock project with requirements"""
        project = Mock(spec=Project)
        project.id = "test-project-id"
        project.name = "Test Project"
        
        # Mock requirements
        req1 = Mock(spec=Requirement)
        req1.object_name = "chair"
        req2 = Mock(spec=Requirement)
        req2.object_name = "table"
        
        project.requirements = [req1, req2]
        return project
    
    @pytest.fixture
    def upload_service(self, mock_db):
        """Create upload service with mocked dependencies"""
        with patch('app.services.upload_service.DetectionService') as mock_detection_service:
            service = UploadService(mock_db)
            service.detection_service = mock_detection_service.return_value
            return service
    
    @pytest.fixture
    def sample_upload_file(self):
        """Create a sample upload file for testing"""
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        upload_file = UploadFile(
            filename="test_image.jpg",
            file=img_bytes
        )
        return upload_file
    
    @pytest.mark.asyncio
    async def test_process_uploads_success(self, upload_service, mock_db, mock_project, sample_upload_file):
        """Test successful upload processing"""
        # Setup mocks
        mock_db.query.return_value.filter.return_value.first.return_value = mock_project
        
        # Mock detection results
        detected_objects = [
            DetectedObject("chair", 0.8, [10, 20, 30, 40]),
            DetectedObject("table", 0.7, [50, 60, 70, 80])
        ]
        upload_service.detection_service.detect_objects = AsyncMock(return_value=detected_objects)
        upload_service.detection_service.filter_relevant_objects.return_value = detected_objects
        
        # Mock file saving
        with patch.object(upload_service, '_save_file') as mock_save_file:
            mock_save_file.return_value = "/fake/path/test_image.jpg"
            
            with patch.object(upload_service, '_store_detections') as mock_store:
                mock_store.return_value = None
                
                # Test upload processing
                result = await upload_service.process_uploads("test-project-id", [sample_upload_file])
                
                assert result.project_id == "test-project-id"
                assert len(result.uploaded_files) == 1
                assert len(result.detection_results) == 1
                assert result.total_objects_detected == 2
                assert result.processing_summary["total_files_uploaded"] == 1
    
    @pytest.mark.asyncio
    async def test_process_uploads_project_not_found(self, upload_service, mock_db, sample_upload_file):
        """Test upload processing with non-existent project"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await upload_service.process_uploads("nonexistent-project", [sample_upload_file])
        
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_validate_files_success(self, upload_service, sample_upload_file):
        """Test successful file validation"""
        validated = await upload_service._validate_files([sample_upload_file])
        
        assert len(validated) == 1
        assert validated[0] == sample_upload_file
    
    @pytest.mark.asyncio
    async def test_validate_files_no_files(self, upload_service):
        """Test validation with no files"""
        with pytest.raises(HTTPException) as exc_info:
            await upload_service._validate_files([])
        
        assert exc_info.value.status_code == 400
        assert "No files provided" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_validate_files_too_many(self, upload_service, sample_upload_file):
        """Test validation with too many files"""
        files = [sample_upload_file] * 15  # More than the limit of 10
        
        with pytest.raises(HTTPException) as exc_info:
            await upload_service._validate_files(files)
        
        assert exc_info.value.status_code == 400
        assert "Too many files" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_validate_files_unsupported_format(self, upload_service):
        """Test validation with unsupported file format"""
        # Create a text file instead of image
        text_content = io.BytesIO(b"This is not an image")
        upload_file = UploadFile(
            filename="test.txt",
            file=text_content
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await upload_service._validate_files([upload_file])
        
        assert exc_info.value.status_code == 400
        assert "unsupported format" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_validate_files_too_large(self, upload_service):
        """Test validation with file too large"""
        # Create a large file (mock the size check)
        large_file = Mock(spec=UploadFile)
        large_file.filename = "large_image.jpg"
        large_file.file = Mock()
        large_file.file.tell.return_value = 15 * 1024 * 1024  # 15MB (over 10MB limit)
        large_file.file.seek = Mock()
        
        with pytest.raises(HTTPException) as exc_info:
            await upload_service._validate_files([large_file])
        
        assert exc_info.value.status_code == 400
        assert "too large" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_validate_files_empty_file(self, upload_service):
        """Test validation with empty file"""
        empty_file = Mock(spec=UploadFile)
        empty_file.filename = "empty.jpg"
        empty_file.file = Mock()
        empty_file.file.tell.return_value = 0  # Empty file
        empty_file.file.seek = Mock()
        
        with pytest.raises(HTTPException) as exc_info:
            await upload_service._validate_files([empty_file])
        
        assert exc_info.value.status_code == 400
        assert "empty" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_save_file_success(self, upload_service, sample_upload_file):
        """Test successful file saving"""
        with tempfile.TemporaryDirectory() as temp_dir:
            upload_path = upload_service.upload_base_path / "test" / "images" / "original"
            upload_path.mkdir(parents=True, exist_ok=True)
            
            # Reset file position
            sample_upload_file.file.seek(0)
            
            file_path = await upload_service._save_file(sample_upload_file, upload_path)
            
            assert file_path.exists()
            assert file_path.suffix == '.jpg'
            assert file_path.parent == upload_path
    
    @pytest.mark.asyncio
    async def test_store_detections_success(self, upload_service, mock_db):
        """Test successful detection storage"""
        detected_objects = [
            DetectedObject("chair", 0.8, [10, 20, 30, 40]),
            DetectedObject("table", 0.7, [50, 60, 70, 80])
        ]
        
        await upload_service._store_detections("test-project", "/path/to/image.jpg", detected_objects)
        
        # Verify that detections were added to database
        assert mock_db.add.call_count == 2
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_store_detections_database_error(self, upload_service, mock_db):
        """Test detection storage with database error"""
        mock_db.commit.side_effect = Exception("Database error")
        
        detected_objects = [DetectedObject("chair", 0.8, [10, 20, 30, 40])]
        
        with pytest.raises(RuntimeError, match="Failed to store detection results"):
            await upload_service._store_detections("test-project", "/path/to/image.jpg", detected_objects)
        
        mock_db.rollback.assert_called_once()
    
    def test_get_project_images_success(self, upload_service):
        """Test getting project images"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock project directory with images
            project_path = upload_service.upload_base_path / "test-project" / "images" / "original"
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Create test image files
            (project_path / "image1.jpg").touch()
            (project_path / "image2.png").touch()
            (project_path / "not_image.txt").touch()  # Should be ignored
            
            images = upload_service.get_project_images("test-project")
            
            assert len(images) == 2
            assert any("image1.jpg" in img for img in images)
            assert any("image2.png" in img for img in images)
            assert not any("not_image.txt" in img for img in images)
    
    def test_get_project_images_no_directory(self, upload_service):
        """Test getting project images when directory doesn't exist"""
        images = upload_service.get_project_images("nonexistent-project")
        
        assert images == []
    
    def test_get_project_images_error_handling(self, upload_service):
        """Test error handling in get_project_images"""
        with patch('pathlib.Path.iterdir', side_effect=Exception("Access denied")):
            images = upload_service.get_project_images("test-project")
            
            assert images == []