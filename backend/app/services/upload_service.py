import os
import shutil
import logging
import time
from typing import List, Optional
from pathlib import Path
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.models.project import Project, Detection
from app.services.detection_service import DetectionService, DetectedObject
from app.schemas.upload import DetectionResult, DetectedObjectResponse, UploadResponse
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class UploadService:
    def __init__(self, db: Session):
        self.db = db
        self.detection_service = DetectionService()
        self.upload_base_path = Path("uploads/projects")
        self.allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
        # Ensure upload directory exists
        self.upload_base_path.mkdir(parents=True, exist_ok=True)
    
    async def process_uploads(self, project_id: str, files: List[UploadFile]) -> UploadResponse:
        """
        Process uploaded images for a project
        
        Args:
            project_id: ID of the project
            files: List of uploaded files
            
        Returns:
            UploadResponse with detection results
        """
        try:
            # Verify project exists
            project = self.db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
            
            # Validate files
            validated_files = await self._validate_files(files)
            
            # Create project upload directory
            project_upload_path = self.upload_base_path / project_id / "images" / "original"
            project_upload_path.mkdir(parents=True, exist_ok=True)
            
            uploaded_files = []
            detection_results = []
            total_objects = 0
            
            # Process each file
            for file in validated_files:
                try:
                    # Save file
                    file_path = await self._save_file(file, project_upload_path)
                    uploaded_files.append(str(file_path))
                    
                    # Detect objects
                    start_time = time.time()
                    detected_objects = await self.detection_service.detect_objects(str(file_path))
                    processing_time = time.time() - start_time
                    
                    # Get project requirements for filtering
                    requirements = [req.object_name for req in project.requirements]
                    relevant_objects = self.detection_service.filter_relevant_objects(detected_objects, requirements)
                    
                    # Store detections in database
                    await self._store_detections(project_id, str(file_path), relevant_objects)
                    
                    # Create detection result
                    detection_result = DetectionResult(
                        image_path=str(file_path),
                        filename=file.filename,
                        detected_objects=[
                            DetectedObjectResponse(
                                name=obj.name,
                                confidence=obj.confidence,
                                bbox=obj.bbox
                            ) for obj in relevant_objects
                        ],
                        processing_time=processing_time,
                        created_at=datetime.now()
                    )
                    
                    detection_results.append(detection_result)
                    total_objects += len(relevant_objects)
                    
                    logger.info(f"Processed {file.filename}: {len(relevant_objects)} relevant objects detected")
                    
                except Exception as e:
                    logger.error(f"Error processing file {file.filename}: {str(e)}")
                    # Continue with other files even if one fails
                    continue
            
            # Create processing summary
            processing_summary = {
                "total_files_uploaded": len(uploaded_files),
                "total_files_processed": len(detection_results),
                "total_objects_detected": total_objects,
                "average_processing_time": sum(r.processing_time for r in detection_results) / len(detection_results) if detection_results else 0
            }
            
            return UploadResponse(
                project_id=project_id,
                uploaded_files=uploaded_files,
                detection_results=detection_results,
                total_objects_detected=total_objects,
                processing_summary=processing_summary
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing uploads for project {project_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Upload processing failed: {str(e)}")
    
    async def _validate_files(self, files: List[UploadFile]) -> List[UploadFile]:
        """Validate uploaded files"""
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        if len(files) > 10:  # Reasonable limit
            raise HTTPException(status_code=400, detail="Too many files. Maximum 10 files allowed")
        
        validated_files = []
        
        for file in files:
            # Check file extension
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in self.allowed_extensions:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File {file.filename} has unsupported format. Allowed: {', '.join(self.allowed_extensions)}"
                )
            
            # Check file size
            file.file.seek(0, 2)  # Seek to end
            file_size = file.file.tell()
            file.file.seek(0)  # Reset to beginning
            
            if file_size > self.max_file_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} is too large. Maximum size: {self.max_file_size // (1024*1024)}MB"
                )
            
            if file_size == 0:
                raise HTTPException(status_code=400, detail=f"File {file.filename} is empty")
            
            validated_files.append(file)
        
        return validated_files
    
    async def _save_file(self, file: UploadFile, upload_path: Path) -> Path:
        """Save uploaded file to disk"""
        try:
            # Generate unique filename to avoid conflicts
            file_ext = Path(file.filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = upload_path / unique_filename
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"Saved file: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving file {file.filename}: {str(e)}")
            raise RuntimeError(f"Failed to save file: {str(e)}")
    
    async def _store_detections(self, project_id: str, image_path: str, detected_objects: List[DetectedObject]):
        """Store detection results in database"""
        try:
            for obj in detected_objects:
                detection = Detection(
                    project_id=project_id,
                    image_path=image_path,
                    object_name=obj.name,
                    confidence=obj.confidence,
                    bbox_x=obj.bbox[0],
                    bbox_y=obj.bbox[1],
                    bbox_width=obj.bbox[2],
                    bbox_height=obj.bbox[3]
                )
                self.db.add(detection)
            
            self.db.commit()
            logger.info(f"Stored {len(detected_objects)} detections for project {project_id}")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error storing detections: {str(e)}")
            raise RuntimeError(f"Failed to store detection results: {str(e)}")
    
    def get_project_images(self, project_id: str) -> List[str]:
        """Get list of uploaded images for a project"""
        try:
            project_path = self.upload_base_path / project_id / "images" / "original"
            if not project_path.exists():
                return []
            
            image_files = []
            for file_path in project_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in self.allowed_extensions:
                    image_files.append(str(file_path))
            
            return sorted(image_files)
            
        except Exception as e:
            logger.error(f"Error getting project images for {project_id}: {str(e)}")
            return []