import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from app.services.progress_service import ProgressService
from app.models.project import Project, Requirement, Detection
from app.schemas.project import ProgressResponse, RequirementMatch, DetectionSummary
from datetime import datetime

class TestProgressService:
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def progress_service(self, mock_db):
        return ProgressService(mock_db)
    
    @pytest.fixture
    def sample_project(self):
        project = Mock(spec=Project)
        project.id = "test-project-id"
        project.name = "Test Project"
        
        # Mock requirements
        req1 = Mock(spec=Requirement)
        req1.object_name = "chair"
        req2 = Mock(spec=Requirement)
        req2.object_name = "table"
        req3 = Mock(spec=Requirement)
        req3.object_name = "lamp"
        
        project.requirements = [req1, req2, req3]
        
        # Mock detections
        det1 = Mock(spec=Detection)
        det1.object_name = "chair"
        det1.confidence = 0.85
        
        det2 = Mock(spec=Detection)
        det2.object_name = "chair"
        det2.confidence = 0.92
        
        det3 = Mock(spec=Detection)
        det3.object_name = "table"
        det3.confidence = 0.78
        
        project.detections = [det1, det2, det3]
        
        return project
    
    @pytest.mark.asyncio
    async def test_calculate_project_progress_success(self, progress_service, mock_db, sample_project):
        """Test successful progress calculation"""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = sample_project
        
        # Execute
        result = await progress_service.calculate_project_progress("test-project-id")
        
        # Assert
        assert result is not None
        assert isinstance(result, ProgressResponse)
        assert result.project_id == "test-project-id"
        assert result.completion_percentage == 66.67  # 2 out of 3 requirements detected
        assert len(result.requirement_matches) == 3
        
        # Check requirement matches
        chair_match = next(m for m in result.requirement_matches if m.requirement == "chair")
        assert chair_match.detected is True
        assert chair_match.confidence == 0.92  # Max confidence
        assert chair_match.count == 2
        
        table_match = next(m for m in result.requirement_matches if m.requirement == "table")
        assert table_match.detected is True
        assert table_match.confidence == 0.78
        assert table_match.count == 1
        
        lamp_match = next(m for m in result.requirement_matches if m.requirement == "lamp")
        assert lamp_match.detected is False
        assert lamp_match.confidence is None
        assert lamp_match.count == 0
        
        # Check detection summary
        assert result.detection_summary.total_objects_detected == 3
        assert set(result.detection_summary.unique_objects) == {"chair", "table"}
        assert result.detection_summary.average_confidence == 0.85  # (0.85 + 0.92 + 0.78) / 3
    
    @pytest.mark.asyncio
    async def test_calculate_project_progress_project_not_found(self, progress_service, mock_db):
        """Test progress calculation when project doesn't exist"""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Execute
        result = await progress_service.calculate_project_progress("nonexistent-id")
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_calculate_project_progress_no_requirements(self, progress_service, mock_db):
        """Test progress calculation when project has no requirements"""
        # Setup
        project = Mock(spec=Project)
        project.id = "test-project-id"
        project.requirements = []
        project.detections = []
        
        mock_db.query.return_value.filter.return_value.first.return_value = project
        
        # Execute
        result = await progress_service.calculate_project_progress("test-project-id")
        
        # Assert
        assert result is not None
        assert result.completion_percentage == 0.0
        assert len(result.requirement_matches) == 0
        assert result.detection_summary.total_objects_detected == 0
    
    @pytest.mark.asyncio
    async def test_calculate_project_progress_no_detections(self, progress_service, mock_db):
        """Test progress calculation when project has no detections"""
        # Setup
        project = Mock(spec=Project)
        project.id = "test-project-id"
        
        req1 = Mock(spec=Requirement)
        req1.object_name = "chair"
        req2 = Mock(spec=Requirement)
        req2.object_name = "table"
        
        project.requirements = [req1, req2]
        project.detections = []
        
        mock_db.query.return_value.filter.return_value.first.return_value = project
        
        # Execute
        result = await progress_service.calculate_project_progress("test-project-id")
        
        # Assert
        assert result is not None
        assert result.completion_percentage == 0.0
        assert len(result.requirement_matches) == 2
        
        for match in result.requirement_matches:
            assert match.detected is False
            assert match.confidence is None
            assert match.count == 0
    
    def test_calculate_requirement_matches(self, progress_service):
        """Test requirement matching logic"""
        # Setup
        requirements = ["chair", "table", "lamp"]
        
        det1 = Mock(spec=Detection)
        det1.object_name = "chair"
        det1.confidence = 0.85
        
        det2 = Mock(spec=Detection)
        det2.object_name = "CHAIR"  # Test case insensitivity
        det2.confidence = 0.92
        
        det3 = Mock(spec=Detection)
        det3.object_name = "table"
        det3.confidence = 0.78
        
        detections = [det1, det2, det3]
        
        # Execute
        matches = progress_service._calculate_requirement_matches(requirements, detections)
        
        # Assert
        assert len(matches) == 3
        
        chair_match = next(m for m in matches if m.requirement == "chair")
        assert chair_match.detected is True
        assert chair_match.confidence == 0.92  # Max confidence
        assert chair_match.count == 2
        
        table_match = next(m for m in matches if m.requirement == "table")
        assert table_match.detected is True
        assert table_match.confidence == 0.78
        assert table_match.count == 1
        
        lamp_match = next(m for m in matches if m.requirement == "lamp")
        assert lamp_match.detected is False
        assert lamp_match.confidence is None
        assert lamp_match.count == 0
    
    def test_calculate_completion_percentage(self, progress_service):
        """Test completion percentage calculation"""
        # Test with mixed matches
        matches = [
            RequirementMatch(requirement="chair", detected=True, confidence=0.9, count=1),
            RequirementMatch(requirement="table", detected=True, confidence=0.8, count=1),
            RequirementMatch(requirement="lamp", detected=False, confidence=None, count=0),
            RequirementMatch(requirement="sofa", detected=False, confidence=None, count=0)
        ]
        
        percentage = progress_service._calculate_completion_percentage(matches)
        assert percentage == 50.0  # 2 out of 4
        
        # Test with all detected
        all_detected = [
            RequirementMatch(requirement="chair", detected=True, confidence=0.9, count=1),
            RequirementMatch(requirement="table", detected=True, confidence=0.8, count=1)
        ]
        
        percentage = progress_service._calculate_completion_percentage(all_detected)
        assert percentage == 100.0
        
        # Test with none detected
        none_detected = [
            RequirementMatch(requirement="chair", detected=False, confidence=None, count=0),
            RequirementMatch(requirement="table", detected=False, confidence=None, count=0)
        ]
        
        percentage = progress_service._calculate_completion_percentage(none_detected)
        assert percentage == 0.0
        
        # Test with empty list
        percentage = progress_service._calculate_completion_percentage([])
        assert percentage == 0.0
    
    def test_generate_detection_summary(self, progress_service):
        """Test detection summary generation"""
        # Setup detections
        det1 = Mock(spec=Detection)
        det1.object_name = "chair"
        det1.confidence = 0.85
        
        det2 = Mock(spec=Detection)
        det2.object_name = "chair"
        det2.confidence = 0.92
        
        det3 = Mock(spec=Detection)
        det3.object_name = "table"
        det3.confidence = 0.78
        
        detections = [det1, det2, det3]
        
        # Execute
        summary = progress_service._generate_detection_summary(detections)
        
        # Assert
        assert summary.total_objects_detected == 3
        assert set(summary.unique_objects) == {"chair", "table"}
        assert summary.average_confidence == 0.85  # (0.85 + 0.92 + 0.78) / 3
        
        # Test with empty detections
        empty_summary = progress_service._generate_detection_summary([])
        assert empty_summary.total_objects_detected == 0
        assert empty_summary.unique_objects == []
        assert empty_summary.average_confidence == 0.0