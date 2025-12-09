import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import numpy as np
from app.services.detection_service import DetectionService, DetectedObject

class TestDetectionService:
    
    @pytest.fixture
    def detection_service(self):
        """Create a detection service instance for testing"""
        with patch('app.services.detection_service.YOLO') as mock_yolo:
            mock_model = Mock()
            mock_model.names = {0: 'chair', 1: 'table', 2: 'sofa'}
            mock_yolo.return_value = mock_model
            
            service = DetectionService()
            service.model = mock_model
            return service
    
    @pytest.fixture
    def sample_image(self):
        """Create a temporary sample image for testing"""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            # Create a simple test image
            img = Image.new('RGB', (100, 100), color='red')
            img.save(tmp_file.name)
            yield tmp_file.name
        
        # Cleanup
        if os.path.exists(tmp_file.name):
            os.unlink(tmp_file.name)
    
    def test_detection_service_initialization(self):
        """Test that detection service initializes correctly"""
        with patch('app.services.detection_service.YOLO') as mock_yolo:
            mock_model = Mock()
            mock_yolo.return_value = mock_model
            
            service = DetectionService()
            
            mock_yolo.assert_called_once_with('yolov8n.pt')
            assert service.model == mock_model
    
    def test_detection_service_initialization_failure(self):
        """Test that detection service handles initialization failure"""
        with patch('app.services.detection_service.YOLO', side_effect=Exception("Model load failed")):
            with pytest.raises(RuntimeError, match="Could not initialize detection model"):
                DetectionService()
    
    @pytest.mark.asyncio
    async def test_detect_objects_success(self, detection_service, sample_image):
        """Test successful object detection"""
        # Mock YOLO results
        mock_box = Mock()
        mock_box.cls = [0]  # chair class
        mock_box.conf = [0.8]  # 80% confidence
        
        # Mock tensor-like object for xyxy
        mock_tensor = Mock()
        mock_tensor.tolist.return_value = [10.0, 20.0, 50.0, 60.0]
        mock_box.xyxy = [mock_tensor]  # bounding box
        
        mock_boxes = Mock()
        mock_boxes.__iter__ = Mock(return_value=iter([mock_box]))
        
        mock_result = Mock()
        mock_result.boxes = mock_boxes
        
        detection_service.model.return_value = [mock_result]
        
        # Test detection
        results = await detection_service.detect_objects(sample_image)
        
        assert len(results) == 1
        assert results[0].name == 'chair'
        assert results[0].confidence == 0.8
        assert results[0].bbox == [10.0, 20.0, 40.0, 40.0]  # [x, y, width, height]
    
    @pytest.mark.asyncio
    async def test_detect_objects_no_detections(self, detection_service, sample_image):
        """Test detection with no objects found"""
        mock_result = Mock()
        mock_result.boxes = None
        
        detection_service.model.return_value = [mock_result]
        
        results = await detection_service.detect_objects(sample_image)
        
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_detect_objects_low_confidence_filtered(self, detection_service, sample_image):
        """Test that low confidence detections are filtered out"""
        # Mock YOLO results with low confidence
        mock_box = Mock()
        mock_box.cls = [0]  # chair class
        mock_box.conf = [0.2]  # 20% confidence (below 0.3 threshold)
        
        # Mock tensor-like object for xyxy
        mock_tensor = Mock()
        mock_tensor.tolist.return_value = [10.0, 20.0, 50.0, 60.0]
        mock_box.xyxy = [mock_tensor]
        
        mock_boxes = Mock()
        mock_boxes.__iter__ = Mock(return_value=iter([mock_box]))
        
        mock_result = Mock()
        mock_result.boxes = mock_boxes
        
        detection_service.model.return_value = [mock_result]
        
        results = await detection_service.detect_objects(sample_image)
        
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_detect_objects_file_not_found(self, detection_service):
        """Test detection with non-existent file"""
        with pytest.raises(RuntimeError, match="Object detection failed"):
            await detection_service.detect_objects("nonexistent_file.jpg")
    
    @pytest.mark.asyncio
    async def test_detect_objects_processing_error(self, detection_service, sample_image):
        """Test detection with processing error"""
        detection_service.model.side_effect = Exception("Processing failed")
        
        with pytest.raises(RuntimeError, match="Object detection failed"):
            await detection_service.detect_objects(sample_image)
    
    def test_filter_relevant_objects(self, detection_service):
        """Test filtering of relevant objects based on requirements"""
        # Create test detections
        detections = [
            DetectedObject("chair", 0.8, [10, 20, 30, 40]),
            DetectedObject("table", 0.7, [50, 60, 70, 80]),
            DetectedObject("person", 0.9, [90, 100, 110, 120]),  # Not in requirements
        ]
        
        requirements = ["chair", "sofa"]  # Only chair matches
        
        filtered = detection_service.filter_relevant_objects(detections, requirements)
        
        assert len(filtered) == 1
        assert filtered[0].name == "chair"
    
    def test_filter_relevant_objects_with_synonyms(self, detection_service):
        """Test filtering with synonym matching"""
        detections = [
            DetectedObject("couch", 0.8, [10, 20, 30, 40]),
        ]
        
        requirements = ["sofa"]  # Should match "couch"
        
        filtered = detection_service.filter_relevant_objects(detections, requirements)
        
        assert len(filtered) == 1
        assert filtered[0].name == "couch"
    
    def test_objects_match_direct(self, detection_service):
        """Test direct object name matching"""
        assert detection_service._objects_match("chair", "chair") == True
        assert detection_service._objects_match("chair", "table") == False
    
    def test_objects_match_synonyms(self, detection_service):
        """Test synonym matching"""
        assert detection_service._objects_match("couch", "sofa") == True
        assert detection_service._objects_match("sofa", "couch") == True
        assert detection_service._objects_match("tv", "television") == True
    
    def test_objects_match_partial(self, detection_service):
        """Test partial matching"""
        assert detection_service._objects_match("dining table", "table") == True
        assert detection_service._objects_match("table", "dining table") == True
    
    def test_get_supported_objects(self, detection_service):
        """Test getting list of supported objects"""
        supported = detection_service.get_supported_objects()
        
        assert isinstance(supported, list)
        assert len(supported) > 0
        assert 'chair' in supported
        assert 'sofa' in supported