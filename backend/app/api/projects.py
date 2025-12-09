from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.project_service import ProjectService
from app.schemas.project import ProjectCreateRequest, ProjectResponse, ErrorResponse
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new project with requirements.
    
    - **name**: Project name (required, 1-255 characters)
    - **requirements**: List of required objects (required, at least 1 item)
    
    Returns the created project with generated ID and timestamp.
    """
    try:
        service = ProjectService(db)
        project = await service.create_project(project_data)
        logger.info(f"Created project: {project.id}")
        return project
        
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project"
        )

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a project by ID.
    
    - **project_id**: The ID of the project to retrieve
    
    Returns the project with its requirements.
    """
    try:
        service = ProjectService(db)
        project = await service.get_project(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        logger.info(f"Retrieved project: {project_id}")
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve project"
        )

@router.get("/", response_model=List[ProjectResponse])
async def get_all_projects(
    db: Session = Depends(get_db)
):
    """
    Get all projects.
    
    Returns a list of all projects with their requirements.
    """
    try:
        service = ProjectService(db)
        projects = await service.get_all_projects()
        logger.info(f"Retrieved {len(projects)} projects")
        return projects
        
    except Exception as e:
        logger.error(f"Error retrieving all projects: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve projects"
        )