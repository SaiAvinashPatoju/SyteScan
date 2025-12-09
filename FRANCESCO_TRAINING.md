# Francesco Furniture Model Training Guide

This guide explains how to train and integrate a custom YOLOv8 model using the Francesco/furniture-ngpea dataset for enhanced furniture detection.

## Overview

The Francesco furniture dataset contains 4 main classes:
- **furniture** (general furniture items)
- **Chair** (chairs and seating)
- **Sofa** (sofas and couches)
- **Table** (tables and desks)

## Quick Start

### Option 1: Use the Batch Script (Windows)
```bash
# Run the automated training script
train_francesco.bat
```

### Option 2: Manual Training

1. **Install training dependencies:**
```bash
cd backend
pip install -r requirements_training.txt
```

2. **Run the training script:**
```bash
# Quick training (30 epochs, nano model)
python train_francesco_furniture.py

# Custom training options
python train_francesco_furniture.py --model-size m --epochs 50

# Download dataset only (no training)
python train_francesco_furniture.py --download-only
```

## Training Options

### Model Sizes
- `n` (nano): Fastest, smallest, lowest accuracy (~3.2M params)
- `s` (small): Good balance (~11.2M params)
- `m` (medium): Better accuracy (~25.9M params) 
- `l` (large): High accuracy (~43.7M params)
- `x` (extra large): Highest accuracy, slowest (~68.2M params)

### Training Parameters
```bash
python train_francesco_furniture.py \
    --model-size m \
    --epochs 50 \
    --output-dir ./my_training
```

## Integration into SyteScan

After training, integrate the model into your application:

```bash
# Integrate trained model
python integrate_francesco_model.py ./francesco_training/models/francesco_furniture_yolov8n_best.pt

# Test the integrated model
python test_francesco_model.py path/to/test/image.jpg
```

## Expected Performance

Based on the project report, you should expect:
- **mAP50**: 85-95% (target: >85%)
- **Training time**: 30-60 minutes (depending on model size)
- **Classes detected**: furniture, chair, sofa, table

### Performance by Model Size
| Model | mAP50 (Expected) | Speed | Use Case |
|-------|------------------|-------|----------|
| YOLOv8n | ~80-85% | Fastest | Development/Testing |
| YOLOv8s | ~85-88% | Fast | Production (balanced) |
| YOLOv8m | ~88-91% | Medium | Production (accuracy focused) |
| YOLOv8l | ~91-93% | Slow | High accuracy needs |
| YOLOv8x | ~93-95% | Slowest | Maximum accuracy |

## File Structure After Training

```
francesco_training/
├── dataset/
│   ├── train/
│   │   ├── images/
│   │   └── labels/
│   ├── val/
│   │   ├── images/
│   │   └── labels/
│   └── dataset.yaml
└── models/
    ├── francesco_furniture_yolov8n/
    │   ├── weights/
    │   │   ├── best.pt
    │   │   └── last.pt
    │   └── results.png
    └── francesco_furniture_yolov8n_best.pt
```

## Using the Trained Model

### 1. Environment Configuration
Update your `.env` file:
```env
YOLO_MODEL=francesco_furniture.pt
DETECTION_CONFIDENCE=0.6
MODEL_TYPE=francesco_furniture
```

### 2. API Usage
The model will automatically be used by your existing API endpoints:
```bash
# Upload image for furniture detection
curl -X POST "http://localhost:8001/api/upload" \
     -F "file=@furniture_image.jpg"
```

### 3. Programmatic Usage
```python
from app.services.detection_service import DetectionService

detector = DetectionService()
detections = await detector.detect_objects("image.jpg")

for detection in detections:
    print(f"Found {detection.name} with {detection.confidence:.2f} confidence")
```

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   - Reduce batch size: `--batch-size 4`
   - Use smaller model: `--model-size n`

2. **Dataset Download Fails**
   - Check internet connection
   - Try running with `--download-only` first

3. **Low Accuracy**
   - Increase epochs: `--epochs 100`
   - Use larger model: `--model-size m` or `--model-size l`
   - Check dataset quality

4. **PyTorch Compatibility Issues**
   - The script handles PyTorch 2.6+ compatibility automatically
   - If issues persist, downgrade to PyTorch 2.0: `pip install torch==2.0.0`

### Performance Optimization

1. **For Speed**: Use YOLOv8n with confidence threshold 0.4
2. **For Accuracy**: Use YOLOv8m+ with confidence threshold 0.6
3. **For Production**: YOLOv8s provides the best balance

## Advanced Configuration

### Custom Hyperparameters
Edit the training script to modify:
- Learning rate schedules
- Data augmentation settings
- Loss function weights
- Optimizer settings

### Dataset Customization
- Add more furniture classes
- Modify class mappings in `_map_category()`
- Adjust confidence thresholds per class

## Monitoring Training

Training progress is logged to console and saved in:
- `francesco_training/models/[model_name]/results.png`
- Training logs in console output

Key metrics to watch:
- **Box Loss**: Should decrease steadily
- **Class Loss**: Should decrease and stabilize
- **mAP50**: Should increase and plateau above 85%

## Next Steps

After successful training and integration:

1. **Test thoroughly** with various furniture images
2. **Adjust confidence thresholds** based on your use case
3. **Consider ensemble methods** for critical applications
4. **Monitor performance** in production
5. **Retrain periodically** with new data

## Support

For issues or questions:
1. Check the console output for error messages
2. Verify all dependencies are installed
3. Ensure sufficient disk space (>5GB for training)
4. Check GPU memory if using CUDA

The Francesco furniture model should significantly improve furniture detection accuracy compared to the general COCO-trained models, especially for the specific classes: furniture, chairs, sofas, and tables.