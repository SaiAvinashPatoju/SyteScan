from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.project import Project, Requirement, Detection
from app.schemas.project import ProgressResponse, RequirementMatch, DetectionSummary
from typing import Optional, Dict, List
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class ProgressService:
    """Service class for progress comparison and calculation"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def calculate_project_progress(self, project_id: str) -> Optional[ProgressResponse]:
        """Calculate progress for a project by comparing requirements against detections"""
        try:
            # Get project with requirements and detections
            project = self.db.query(Project).filter(Project.id == project_id).first()
            
            if not project:
                logger.warning(f"Project {project_id} not found")
                return None
            
            # Get requirements and detections
            requirements = [req.object_name for req in project.requirements]
            detections = project.detections
            
            if not requirements:
                logger.warning(f"No requirements found for project {project_id}")
                return ProgressResponse(
                    project_id=project_id,
                    completion_percentage=0.0,
                    requirement_matches=[],
                    detection_summary=DetectionSummary(
                        total_objects_detected=0,
                        unique_objects=[],
                        average_confidence=0.0
                    )
                )
            
            # Calculate requirement matches
            requirement_matches = self._calculate_requirement_matches(requirements, detections)
            
            # Calculate completion percentage
            completion_percentage = self._calculate_completion_percentage(requirement_matches)
            
            # Generate detection summary
            detection_summary = self._generate_detection_summary(detections)
            
            return ProgressResponse(
                project_id=project_id,
                completion_percentage=completion_percentage,
                requirement_matches=requirement_matches,
                detection_summary=detection_summary
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Database error calculating progress for project {project_id}: {str(e)}")
            raise Exception("Failed to calculate progress due to database error")
        except Exception as e:
            logger.error(f"Unexpected error calculating progress for project {project_id}: {str(e)}")
            raise Exception("Failed to calculate progress")
    
    def _calculate_requirement_matches(self, requirements: List[str], detections: List[Detection]) -> List[RequirementMatch]:
        """Calculate matches between requirements and detections"""
        # Group detections by object name with confidence scores
        detection_groups = defaultdict(list)
        for detection in detections:
            detection_groups[detection.object_name.lower()].append(detection.confidence)
        
        requirement_matches = []
        
        for requirement in requirements:
            req_lower = requirement.lower()
            
            if req_lower in detection_groups:
                confidences = detection_groups[req_lower]
                requirement_matches.append(RequirementMatch(
                    requirement=requirement,
                    detected=True,
                    confidence=max(confidences),  # Use highest confidence
                    count=len(confidences)
                ))
            else:
                requirement_matches.append(RequirementMatch(
                    requirement=requirement,
                    detected=False,
                    confidence=None,
                    count=0
                ))
        
        return requirement_matches
    
    def _calculate_completion_percentage(self, requirement_matches: List[RequirementMatch]) -> float:
        """Calculate completion percentage based on requirement matches"""
        if not requirement_matches:
            return 0.0
        
        detected_count = sum(1 for match in requirement_matches if match.detected)
        total_count = len(requirement_matches)
        
        return round((detected_count / total_count) * 100, 2)
    
    def _generate_detection_summary(self, detections: List[Detection]) -> DetectionSummary:
        """Generate summary of all detections"""
        if not detections:
            return DetectionSummary(
                total_objects_detected=0,
                unique_objects=[],
                average_confidence=0.0
            )
        
        # Get unique objects and calculate average confidence
        unique_objects = list(set(detection.object_name for detection in detections))
        total_confidence = sum(detection.confidence for detection in detections)
        average_confidence = round(total_confidence / len(detections), 3)
        
        return DetectionSummary(
            total_objects_detected=len(detections),
            unique_objects=sorted(unique_objects),
            average_confidence=average_confidence
        )