from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.upload_service import UploadService
from app.schemas.upload import UploadResponse, UploadError
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["upload"])

@router.post("/{project_id}/upload", response_model=UploadResponse)
async def upload_images(
    project_id: str,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process images for object detection
    
    - **project_id**: ID of the project to upload images for
    - **files**: List of image files (JPEG, PNG, BMP, TIFF)
    
    Returns detection results for all uploaded images.
    """
    try:
        service = UploadService(db)
        result = await service.process_uploads(project_id, files)
        
        logger.info(f"Successfully processed {len(files)} files for project {project_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during upload processing"
        )

@router.get("/{project_id}/images")
async def get_project_images(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Get list of uploaded images for a project
    
    - **project_id**: ID of the project
    
    Returns list of image file paths.
    """
    try:
        service = UploadService(db)
        images = service.get_project_images(project_id)
        
        return {
            "project_id": project_id,
            "images": images,
            "count": len(images)
        }
        
    except Exception as e:
        logger.error(f"Error getting images for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve project images"
        )

@router.get("/{project_id}/detections")
async def get_project_detections(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detection results for a project
    
    - **project_id**: ID of the project
    
    Returns detection results and summary.
    """
    try:
        from app.models.project import Detection, Project
        
        # Verify project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        # Get all detections for the project
        detections = db.query(Detection).filter(Detection.project_id == project_id).all()
        
        # Group detections by image
        detections_by_image = {}
        for detection in detections:
            if detection.image_path not in detections_by_image:
                detections_by_image[detection.image_path] = []
            detections_by_image[detection.image_path].append({
                "name": detection.object_name,
                "confidence": detection.confidence,
                "bbox": [detection.bbox_x, detection.bbox_y, detection.bbox_width, detection.bbox_height]
            })
        
        return {
            "project_id": project_id,
            "total_detections": len(detections),
            "images_processed": len(detections_by_image),
            "detections_by_image": detections_by_image
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting detections for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve project detections"
        )