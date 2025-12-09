#!/usr/bin/env python3
"""
Francesco Furniture Model Integration Script

This script helps integrate a trained Francesco furniture model
into the existing SyteScan application.
"""

import os
import sys
import logging
import shutil
from pathlib import Path
from typing import Optional
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FrancescoModelIntegrator:
    """Integrates Francesco furniture model into SyteScan"""
    
    def __init__(self):
        self.backend_dir = Path(__file__).parent
        self.app_dir = self.backend_dir / "app"
        
    def integrate_model(self, model_path: str, model_name: str = "francesco_furniture.pt") -> bool:
        """
        Integrate trained Francesco model into the application
        
        Args:
            model_path: Path to trained model file
            model_name: Name for the model in the application
            
        Returns:
            bool: True if successful
        """
        try:
            model_path = Path(model_path)
            if not model_path.exists():
                logger.error(f"Model file not found: {model_path}")
                return False
            
            # Copy model to backend directory
            target_path = self.backend_dir / model_name
            shutil.copy2(model_path, target_path)
            logger.info(f"Model copied to: {target_path}")
            
            # Update detection service for Francesco classes
            self._update_detection_service()
            
            # Create environment configuration
            self._create_env_config(model_name)
            
            logger.info("Francesco model integration completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Integration failed: {str(e)}")
            return False
    
    def _update_detection_service(self):
        """Update detection service to support Francesco furniture classes"""
        detection_service_path = self.app_dir / "services" / "detection_service.py"
        
        # Read current file
        with open(detection_service_path, 'r') as f:
            content = f.read()
        
        # Add Francesco-specific configuration
        francesco_config = '''
        # Francesco furniture dataset classes
        self.francesco_classes = {
            0: "furniture",
            1: "chair", 
            2: "sofa",
            3: "table"
        }
        
        # Enhanced furniture detection for Francesco model
        self.furniture_objects = {
            'chair', 'sofa', 'table', 'furniture', 'couch', 'dining table',
            'bed', 'desk', 'cabinet', 'shelf', 'dresser', 'nightstand'
        }'''
        
        # Insert after the existing relevant_objects definition
        if "self.francesco_classes" not in content:
            # Find insertion point
            insertion_point = content.find("self.relevant_objects = {")
            if insertion_point != -1:
                # Find end of relevant_objects definition
                end_point = content.find("}", insertion_point) + 1
                # Insert Francesco config after
                content = content[:end_point] + "\n" + francesco_config + content[end_point:]
                
                # Write updated content
                with open(detection_service_path, 'w') as f:
                    f.write(content)
                
                logger.info("Updated detection service with Francesco classes")
    
    def _create_env_config(self, model_name: str):
        """Create environment configuration for Francesco model"""
        env_example_path = self.backend_dir / ".env.example"
        
        francesco_config = f"""
# Francesco Furniture Model Configuration
YOLO_MODEL={model_name}
DETECTION_CONFIDENCE=0.6
MODEL_TYPE=francesco_furniture

# Francesco model supports these classes:
# 0: furniture (general)
# 1: chair
# 2: sofa  
# 3: table
"""
        
        # Append to .env.example if it exists
        if env_example_path.exists():
            with open(env_example_path, 'a') as f:
                f.write(francesco_config)
        else:
            with open(env_example_path, 'w') as f:
                f.write(francesco_config.strip())
        
        logger.info(f"Updated environment configuration in {env_example_path}")
        
        # Also create a .env.francesco file
        env_francesco_path = self.backend_dir / ".env.francesco"
        with open(env_francesco_path, 'w') as f:
            f.write(francesco_config.strip())
        
        logger.info(f"Created Francesco-specific config: {env_francesco_path}")
    
    def create_test_script(self) -> str:
        """Create a test script for the Francesco model"""
        test_script_content = '''#!/usr/bin/env python3
"""
Test script for Francesco furniture model
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from app.services.detection_service import DetectionService

async def test_francesco_model(image_path: str):
    """Test Francesco model on an image"""
    try:
        # Initialize detection service
        detector = DetectionService()
        
        # Run detection
        detections = await detector.detect_objects(image_path)
        
        print(f"\\nDetected {len(detections)} objects in {image_path}:")
        print("-" * 50)
        
        for i, detection in enumerate(detections, 1):
            print(f"{i}. {detection.name.title()}")
            print(f"   Confidence: {detection.confidence:.3f}")
            print(f"   Bounding Box: {detection.bbox}")
            print()
        
        # Filter for furniture items
        furniture_items = [d for d in detections if d.name in ['chair', 'sofa', 'table', 'furniture']]
        print(f"Furniture items found: {len(furniture_items)}")
        
        return detections
        
    except Exception as e:
        print(f"Error testing model: {str(e)}")
        return []

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_francesco_model.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    if not Path(image_path).exists():
        print(f"Image file not found: {image_path}")
        sys.exit(1)
    
    asyncio.run(test_francesco_model(image_path))
'''
        
        test_script_path = self.backend_dir / "test_francesco_model.py"
        with open(test_script_path, 'w') as f:
            f.write(test_script_content)
        
        logger.info(f"Created test script: {test_script_path}")
        return str(test_script_path)
    
    def show_usage_instructions(self, model_name: str):
        """Show instructions for using the integrated model"""
        print(f"\n{'='*60}")
        print("FRANCESCO MODEL INTEGRATION COMPLETE!")
        print(f"{'='*60}")
        print(f"Model file: {model_name}")
        print()
        print("To use the Francesco furniture model:")
        print()
        print("1. Update your environment configuration:")
        print(f"   - Copy .env.francesco to .env")
        print(f"   - Or set YOLO_MODEL={model_name} in your .env file")
        print()
        print("2. Restart your FastAPI server:")
        print("   python main.py")
        print()
        print("3. Test the model:")
        print("   python test_francesco_model.py <image_path>")
        print()
        print("4. The model detects these furniture classes:")
        print("   - General furniture")
        print("   - Chairs")
        print("   - Sofas/Couches") 
        print("   - Tables")
        print()
        print("5. API endpoint will now use Francesco model:")
        print("   POST /api/upload with furniture images")
        print(f"{'='*60}")


def main():
    """Main integration script"""
    parser = argparse.ArgumentParser(description='Integrate Francesco furniture model')
    parser.add_argument('model_path', help='Path to trained Francesco model file')
    parser.add_argument('--model-name', default='francesco_furniture.pt',
                       help='Name for model in application (default: francesco_furniture.pt)')
    
    args = parser.parse_args()
    
    try:
        integrator = FrancescoModelIntegrator()
        
        # Integrate model
        success = integrator.integrate_model(args.model_path, args.model_name)
        
        if success:
            # Create test script
            integrator.create_test_script()
            
            # Show usage instructions
            integrator.show_usage_instructions(args.model_name)
        else:
            logger.error("Model integration failed!")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Integration failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()