#!/usr/bin/env python3
"""
Quick Training Script for Francesco Furniture Dataset
Based on the ProgressAnalyzer project specifications

This script provides a streamlined way to train a custom YOLOv8 model
on the Francesco/furniture-ngpea dataset for furniture detection.

Classes: furniture, Chair, Sofa, Table
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from typing import Dict, Any
import yaml
import torch
from ultralytics import YOLO
from datasets import load_dataset
import requests
from PIL import Image
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FrancescoFurnitureTrainer:
    """Quick trainer for Francesco furniture dataset"""
    
    def __init__(self, output_dir: str = "./francesco_training"):
        self.output_dir = Path(output_dir)
        self.dataset_dir = self.output_dir / "dataset"
        self.models_dir = self.output_dir / "models"
        
        # Create directories
        self.output_dir.mkdir(exist_ok=True)
        self.dataset_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        
        # Francesco dataset classes (based on project report)
        self.classes = {
            0: "furniture",
            1: "Chair", 
            2: "Sofa",
            3: "Table"
        }
        
        logger.info(f"Initialized trainer with output directory: {self.output_dir}")
    
    def download_dataset(self) -> bool:
        """
        Download and prepare the Francesco furniture dataset
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Downloading Francesco/furniture-ngpea dataset from Hugging Face...")
            
            # Load dataset from Hugging Face
            dataset = load_dataset("Francesco/furniture-ngpea", trust_remote_code=True)
            
            logger.info(f"Dataset loaded successfully. Available splits: {list(dataset.keys())}")
            
            # Create YOLO format directories
            for split in ['train', 'val']:
                (self.dataset_dir / split / 'images').mkdir(parents=True, exist_ok=True)
                (self.dataset_dir / split / 'labels').mkdir(parents=True, exist_ok=True)
            
            # Process dataset splits
            train_data = dataset.get('train', dataset.get('training', None))
            val_data = dataset.get('validation', dataset.get('val', None))
            
            if train_data is None:
                # If no validation split, create one from train
                logger.info("No validation split found, creating 80/20 split from train data")
                full_data = dataset[list(dataset.keys())[0]]
                train_size = int(0.8 * len(full_data))
                train_data = full_data.select(range(train_size))
                val_data = full_data.select(range(train_size, len(full_data)))
            
            # Process training data
            logger.info("Processing training data...")
            self._process_split(train_data, 'train')
            
            # Process validation data
            logger.info("Processing validation data...")
            self._process_split(val_data, 'val')
            
            # Create dataset YAML file
            self._create_dataset_yaml()
            
            logger.info("Dataset preparation completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download/prepare dataset: {str(e)}")
            return False
    
    def _process_split(self, data, split_name: str):
        """Process a dataset split and convert to YOLO format"""
        images_dir = self.dataset_dir / split_name / 'images'
        labels_dir = self.dataset_dir / split_name / 'labels'
        
        for idx, item in enumerate(data):
            try:
                # Get image
                image = item.get('image', item.get('img', None))
                if image is None:
                    logger.warning(f"No image found in item {idx}")
                    continue
                
                # Save image
                image_filename = f"{split_name}_{idx:06d}.jpg"
                image_path = images_dir / image_filename
                
                if isinstance(image, Image.Image):
                    image.save(image_path, 'JPEG')
                else:
                    # Handle other image formats
                    Image.fromarray(image).save(image_path, 'JPEG')
                
                # Get annotations
                annotations = item.get('objects', item.get('annotations', {}))
                
                # Create YOLO format label file
                label_filename = f"{split_name}_{idx:06d}.txt"
                label_path = labels_dir / label_filename
                
                with open(label_path, 'w') as f:
                    if isinstance(annotations, dict):
                        # Handle different annotation formats
                        bboxes = annotations.get('bbox', annotations.get('bboxes', []))
                        categories = annotations.get('category', annotations.get('categories', []))
                        
                        if not isinstance(bboxes, list):
                            bboxes = [bboxes] if bboxes is not None else []
                        if not isinstance(categories, list):
                            categories = [categories] if categories is not None else []
                        
                        # Ensure we have matching bbox and category counts
                        min_len = min(len(bboxes), len(categories)) if categories else len(bboxes)
                        
                        for i in range(min_len):
                            bbox = bboxes[i]
                            category = categories[i] if i < len(categories) else 0
                            
                            # Convert bbox to YOLO format (normalized xywh)
                            if len(bbox) == 4:
                                x, y, w, h = bbox
                                # Normalize coordinates (assuming they're in pixel coordinates)
                                img_w, img_h = image.size if hasattr(image, 'size') else (640, 640)
                                
                                # Convert to center coordinates and normalize
                                x_center = (x + w/2) / img_w
                                y_center = (y + h/2) / img_h
                                width = w / img_w
                                height = h / img_h
                                
                                # Ensure values are within [0, 1]
                                x_center = max(0, min(1, x_center))
                                y_center = max(0, min(1, y_center))
                                width = max(0, min(1, width))
                                height = max(0, min(1, height))
                                
                                # Map category to our class system
                                class_id = self._map_category(category)
                                
                                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
                
                if idx % 100 == 0:
                    logger.info(f"Processed {idx} items in {split_name} split")
                    
            except Exception as e:
                logger.warning(f"Failed to process item {idx} in {split_name}: {str(e)}")
                continue
    
    def _map_category(self, category) -> int:
        """Map dataset category to our class system"""
        if isinstance(category, str):
            category_lower = category.lower()
            if 'chair' in category_lower:
                return 1
            elif 'sofa' in category_lower or 'couch' in category_lower:
                return 2
            elif 'table' in category_lower:
                return 3
            else:
                return 0  # general furniture
        elif isinstance(category, int):
            # Assume it's already mapped correctly
            return min(category, 3)
        else:
            return 0
    
    def _create_dataset_yaml(self):
        """Create YOLO dataset configuration file"""
        yaml_content = {
            'path': str(self.dataset_dir.absolute()),
            'train': 'train/images',
            'val': 'val/images',
            'nc': len(self.classes),
            'names': list(self.classes.values())
        }
        
        yaml_path = self.dataset_dir / 'dataset.yaml'
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_content, f, default_flow_style=False)
        
        logger.info(f"Created dataset YAML at: {yaml_path}")
    
    def train_model(self, 
                   model_size: str = 'n',
                   epochs: int = 50,
                   batch_size: int = 8,
                   img_size: int = 640,
                   patience: int = 10) -> str:
        """
        Train YOLOv8 model on Francesco furniture dataset
        
        Args:
            model_size: Model size ('n', 's', 'm', 'l', 'x')
            epochs: Number of training epochs
            batch_size: Training batch size
            img_size: Input image size
            patience: Early stopping patience
            
        Returns:
            str: Path to trained model
        """
        try:
            logger.info(f"Starting training with YOLOv8{model_size} model...")
            
            # Initialize model
            model_name = f"yolov8{model_size}.pt"
            model = YOLO(model_name)
            
            # Training configuration
            train_config = {
                'data': str(self.dataset_dir / 'dataset.yaml'),
                'epochs': epochs,
                'batch': batch_size,
                'imgsz': img_size,
                'patience': patience,
                'project': str(self.models_dir),
                'name': f'francesco_furniture_yolov8{model_size}',
                'exist_ok': True,
                'verbose': True,
                
                # Optimized hyperparameters from project report
                'lr0': 0.001,
                'lrf': 0.01,
                'momentum': 0.937,
                'weight_decay': 0.0005,
                'optimizer': 'AdamW',
                
                # Loss weights
                'box': 7.5,
                'cls': 0.5,
                'dfl': 1.5,
                
                # Data augmentation
                'hsv_h': 0.015,
                'hsv_s': 0.7,
                'hsv_v': 0.4,
                'fliplr': 0.5,
                'mosaic': 1.0,
            }
            
            # Start training
            results = model.train(**train_config)
            
            # Get best model path
            best_model_path = self.models_dir / f'francesco_furniture_yolov8{model_size}' / 'weights' / 'best.pt'
            
            logger.info(f"Training completed! Best model saved at: {best_model_path}")
            
            # Copy best model to easy access location
            final_model_path = self.models_dir / f'francesco_furniture_yolov8{model_size}_best.pt'
            if best_model_path.exists():
                import shutil
                shutil.copy2(best_model_path, final_model_path)
                logger.info(f"Model copied to: {final_model_path}")
                return str(final_model_path)
            
            return str(best_model_path)
            
        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            raise
    
    def validate_model(self, model_path: str) -> Dict[str, Any]:
        """
        Validate trained model and return metrics
        
        Args:
            model_path: Path to trained model
            
        Returns:
            Dict containing validation metrics
        """
        try:
            logger.info(f"Validating model: {model_path}")
            
            # Load model
            model = YOLO(model_path)
            
            # Run validation
            results = model.val(data=str(self.dataset_dir / 'dataset.yaml'))
            
            # Extract metrics
            metrics = {
                'mAP50': float(results.box.map50),
                'mAP50-95': float(results.box.map),
                'precision': float(results.box.mp),
                'recall': float(results.box.mr),
                'f1_score': 2 * (float(results.box.mp) * float(results.box.mr)) / (float(results.box.mp) + float(results.box.mr)) if (float(results.box.mp) + float(results.box.mr)) > 0 else 0
            }
            
            logger.info(f"Validation metrics: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return {}
    
    def quick_train(self, model_size: str = 'n', epochs: int = 30) -> str:
        """
        Quick training pipeline - download dataset and train model
        
        Args:
            model_size: Model size ('n', 's', 'm', 'l', 'x')
            epochs: Number of training epochs
            
        Returns:
            str: Path to trained model
        """
        logger.info("Starting quick training pipeline for Francesco furniture dataset...")
        
        # Step 1: Download and prepare dataset
        if not self.download_dataset():
            raise RuntimeError("Failed to download/prepare dataset")
        
        # Step 2: Train model
        model_path = self.train_model(model_size=model_size, epochs=epochs)
        
        # Step 3: Validate model
        metrics = self.validate_model(model_path)
        
        logger.info("Quick training completed successfully!")
        logger.info(f"Final model: {model_path}")
        logger.info(f"Performance: mAP50={metrics.get('mAP50', 'N/A'):.3f}")
        
        return model_path


def main():
    """Main training script"""
    parser = argparse.ArgumentParser(description='Train YOLOv8 on Francesco furniture dataset')
    parser.add_argument('--model-size', choices=['n', 's', 'm', 'l', 'x'], default='n',
                       help='YOLOv8 model size (default: n)')
    parser.add_argument('--epochs', type=int, default=30,
                       help='Number of training epochs (default: 30)')
    parser.add_argument('--output-dir', default='./francesco_training',
                       help='Output directory for training files')
    parser.add_argument('--download-only', action='store_true',
                       help='Only download and prepare dataset, skip training')
    
    args = parser.parse_args()
    
    try:
        # Initialize trainer
        trainer = FrancescoFurnitureTrainer(output_dir=args.output_dir)
        
        if args.download_only:
            # Only download dataset
            logger.info("Downloading dataset only...")
            success = trainer.download_dataset()
            if success:
                logger.info("Dataset download completed successfully!")
            else:
                logger.error("Dataset download failed!")
                sys.exit(1)
        else:
            # Full training pipeline
            model_path = trainer.quick_train(
                model_size=args.model_size,
                epochs=args.epochs
            )
            
            print(f"\n{'='*60}")
            print(f"TRAINING COMPLETED SUCCESSFULLY!")
            print(f"{'='*60}")
            print(f"Model saved at: {model_path}")
            print(f"To use this model in your application:")
            print(f"1. Copy the model file to your backend directory")
            print(f"2. Update your config to use the custom model")
            print(f"{'='*60}")
    
    except KeyboardInterrupt:
        logger.info("Training interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()