from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.progress_service import ProgressService
from app.schemas.project import ProgressResponse, ErrorResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/projects",
    tags=["progress"],
    responses={404: {"model": ErrorResponse}}
)

@router.get("/{project_id}/progress", response_model=ProgressResponse)
async def get_project_progress(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Get progress analysis for a specific project.
    
    This endpoint compares the project's requirements against detected objects
    and returns completion percentage, requirement matches, and detection summary.
    """
    try:
        progress_service = ProgressService(db)
        progress_data = await progress_service.calculate_project_progress(project_id)
        
        if progress_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {project_id} not found"
            )
        
        logger.info(f"Successfully calculated progress for project {project_id}")
        return progress_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting progress for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while calculating progress"
        )