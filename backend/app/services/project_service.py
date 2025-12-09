from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.project import Project, Requirement
from app.schemas.project import ProjectCreateRequest, ProjectResponse
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class ProjectService:
    """Service class for project-related operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_project(self, project_data: ProjectCreateRequest) -> ProjectResponse:
        """Create a new project with requirements"""
        try:
            # Create project
            project = Project(name=project_data.name)
            self.db.add(project)
            self.db.flush()  # Get the project ID without committing
            
            # Create requirements
            requirements = []
            for req_name in project_data.requirements:
                requirement = Requirement(
                    project_id=project.id,
                    object_name=req_name.strip().lower()
                )
                requirements.append(requirement)
                self.db.add(requirement)
            
            # Commit all changes
            self.db.commit()
            self.db.refresh(project)
            
            # Return response with requirements list
            return ProjectResponse(
                id=project.id,
                name=project.name,
                requirements=[req.object_name for req in requirements],
                created_at=project.created_at
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Database error creating project: {str(e)}")
            self.db.rollback()
            raise Exception("Failed to create project due to database error")
        except Exception as e:
            logger.error(f"Unexpected error creating project: {str(e)}")
            self.db.rollback()
            raise Exception("Failed to create project")
    
    async def get_project(self, project_id: str) -> Optional[ProjectResponse]:
        """Get a project by ID with its requirements"""
        try:
            project = self.db.query(Project).filter(Project.id == project_id).first()
            
            if not project:
                return None
            
            # Get requirements for this project
            requirements = [req.object_name for req in project.requirements]
            
            return ProjectResponse(
                id=project.id,
                name=project.name,
                requirements=requirements,
                created_at=project.created_at
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving project {project_id}: {str(e)}")
            raise Exception("Failed to retrieve project due to database error")
        except Exception as e:
            logger.error(f"Unexpected error retrieving project {project_id}: {str(e)}")
            raise Exception("Failed to retrieve project")
    
    async def get_all_projects(self) -> List[ProjectResponse]:
        """Get all projects with their requirements"""
        try:
            projects = self.db.query(Project).all()
            
            result = []
            for project in projects:
                requirements = [req.object_name for req in project.requirements]
                result.append(ProjectResponse(
                    id=project.id,
                    name=project.name,
                    requirements=requirements,
                    created_at=project.created_at
                ))
            
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving all projects: {str(e)}")
            raise Exception("Failed to retrieve projects due to database error")
        except Exception as e:
            logger.error(f"Unexpected error retrieving all projects: {str(e)}")
            raise Exception("Failed to retrieve projects")