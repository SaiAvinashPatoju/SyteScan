import os
import logging
from typing import List, Dict, Any
from ultralytics import YOLO
from PIL import Image
import numpy as np
from pathlib import Path
import torch

logger = logging.getLogger(__name__)

class DetectedObject:
    def __init__(self, name: str, confidence: float, bbox: List[float]):
        self.name = name
        self.confidence = confidence
        self.bbox = bbox  # [x, y, width, height]

class DetectionService:
    def __init__(self):
        self.model = None
        self._load_model()
        
        # YOLO class names that are relevant for construction/interior projects
        self.relevant_objects = {
            'chair', 'couch', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
            'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven',
            'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase',
            'scissors', 'teddy bear', 'hair drier', 'toothbrush', 'bottle',
            'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana',
            'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog',
            'pizza', 'donut', 'cake', 'potted plant', 'sofa'
        }
    
    def _load_model(self):
        """Load YOLOv8 model based on configuration"""
        try:
            from app.config import settings
            model_name = settings.yolo_model
            
            # Validate model name
            valid_models = [
                'yolov8n.pt',    # Nano - fastest, lowest accuracy
                'yolov8s.pt',    # Small - good balance
                'yolov8m.pt',    # Medium - better accuracy
                'yolov8l.pt',    # Large - high accuracy
                'yolov8x.pt',    # Extra Large - highest accuracy
                'yolov8n-seg.pt', # Nano segmentation
                'yolov8s-seg.pt', # Small segmentation
                'yolov8m-seg.pt', # Medium segmentation
                'yolov8l-seg.pt', # Large segmentation
                'yolov8x-seg.pt'  # Extra Large segmentation
            ]
            
            if model_name not in valid_models:
                logger.warning(f"Invalid model name '{model_name}', falling back to yolov8n.pt")
                model_name = 'yolov8n.pt'
            
            # Fix for PyTorch 2.6+ security restrictions
            # Add safe globals for YOLOv8 model loading
            try:
                # Try with safe globals first (PyTorch 2.6+)
                with torch.serialization.safe_globals(['ultralytics.nn.tasks.DetectionModel']):
                    self.model = YOLO(model_name)
            except (AttributeError, TypeError):
                # Fallback for older PyTorch versions or if safe_globals doesn't work
                try:
                    # Add safe globals using the new method
                    torch.serialization.add_safe_globals(['ultralytics.nn.tasks.DetectionModel'])
                    self.model = YOLO(model_name)
                except (AttributeError, TypeError):
                    # Final fallback - load with weights_only=False (less secure but works)
                    logger.warning("Using weights_only=False for YOLOv8 model loading due to PyTorch compatibility")
                    # Monkey patch torch.load temporarily
                    original_load = torch.load
                    torch.load = lambda *args, **kwargs: original_load(*args, **kwargs, weights_only=False)
                    try:
                        self.model = YOLO(model_name)
                    finally:
                        torch.load = original_load
            
            # Log model details
            model_details = {
                'yolov8n.pt': 'Nano (~3.2M params, fastest)',
                'yolov8s.pt': 'Small (~11.2M params, fast)', 
                'yolov8m.pt': 'Medium (~25.9M params, balanced accuracy/speed)',
                'yolov8l.pt': 'Large (~43.7M params, high accuracy)',
                'yolov8x.pt': 'Extra Large (~68.2M params, highest accuracy)'
            }
            
            detail = model_details.get(model_name, 'Custom model')
            logger.info(f"YOLOv8 model '{model_name}' loaded successfully - {detail}")
            
        except Exception as e:
            logger.error(f"Failed to load YOLOv8 model: {str(e)}")
            raise RuntimeError(f"Could not initialize detection model: {str(e)}")
    
    async def detect_objects(self, image_path: str) -> List[DetectedObject]:
        """
        Process image and return detected objects with confidence scores
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of DetectedObject instances
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Run inference
            results = self.model(image_path, verbose=False)
            
            detected_objects = []
            
            # Process results
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get class name
                        class_id = int(box.cls[0])
                        class_name = self.model.names[class_id].lower()
                        
                        # Get confidence
                        confidence = float(box.conf[0])
                        
                        # Get bounding box coordinates (xyxy format)
                        bbox_xyxy = box.xyxy[0].tolist()
                        # Convert to [x, y, width, height] format
                        bbox = [
                            bbox_xyxy[0],  # x
                            bbox_xyxy[1],  # y
                            bbox_xyxy[2] - bbox_xyxy[0],  # width
                            bbox_xyxy[3] - bbox_xyxy[1]   # height
                        ]
                        
                        # Only include objects with reasonable confidence
                        # Medium model typically has better confidence scores, so we can be more selective
                        if confidence > 0.4:
                            detected_objects.append(DetectedObject(
                                name=class_name,
                                confidence=confidence,
                                bbox=bbox
                            ))
            
            logger.info(f"Detected {len(detected_objects)} objects in {image_path}")
            return detected_objects
            
        except Exception as e:
            logger.error(f"Error detecting objects in {image_path}: {str(e)}")
            raise RuntimeError(f"Object detection failed: {str(e)}")
    
    def filter_relevant_objects(self, detections: List[DetectedObject], requirements: List[str]) -> List[DetectedObject]:
        """
        Filter detections to only include objects from requirements list
        
        Args:
            detections: List of all detected objects
            requirements: List of required object names
            
        Returns:
            List of DetectedObject instances that match requirements
        """
        try:
            # Normalize requirement names for matching
            normalized_requirements = [req.lower().strip() for req in requirements]
            
            relevant_detections = []
            
            for detection in detections:
                # Check if detected object matches any requirement
                for requirement in normalized_requirements:
                    if self._objects_match(detection.name, requirement):
                        relevant_detections.append(detection)
                        break
            
            logger.info(f"Filtered {len(relevant_detections)} relevant objects from {len(detections)} total detections")
            return relevant_detections
            
        except Exception as e:
            logger.error(f"Error filtering relevant objects: {str(e)}")
            return detections  # Return all detections if filtering fails
    
    def _objects_match(self, detected_name: str, required_name: str) -> bool:
        """
        Check if a detected object matches a required object name
        
        Args:
            detected_name: Name from YOLO detection
            required_name: Name from requirements list
            
        Returns:
            True if objects match, False otherwise
        """
        # Direct match
        if detected_name == required_name:
            return True
        
        # Handle common synonyms and variations
        synonyms = {
            'sofa': ['couch', 'sofa'],
            'couch': ['couch', 'sofa'],
            'tv': ['tv', 'television'],
            'television': ['tv', 'television'],
            'dining table': ['table', 'dining table'],
            'table': ['table', 'dining table'],
            'chair': ['chair', 'seat'],
            'seat': ['chair', 'seat'],
            'bed': ['bed', 'bedroom'],
            'light': ['lamp', 'light'],
            'lamp': ['lamp', 'light'],
            'fan': ['fan', 'ceiling fan'],
            'window': ['window'],  # YOLO doesn't detect windows well, but we include it
        }
        
        # Check if either name has synonyms that match the other
        for synonym_group in synonyms.values():
            if detected_name in synonym_group and required_name in synonym_group:
                return True
        
        # Partial matching for compound names
        if required_name in detected_name or detected_name in required_name:
            return True
        
        return False
    
    def get_supported_objects(self) -> List[str]:
        """
        Get list of objects that can be detected by the model
        
        Returns:
            List of supported object names
        """
        return list(self.relevant_objects)