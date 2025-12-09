# SyteScan Training Data

This directory contains training datasets for the YOLOv8 object detection model.

## Directory Structure

```
data/
├── sample/           # Small sample dataset (tracked in git)
│   ├── images/      # Sample images for testing
│   └── labels/      # Corresponding YOLO format labels
├── francesco_training/  # Full training dataset (gitignored)
│   ├── train/
│   │   ├── images/
│   │   └── labels/
│   └── val/
│       ├── images/
│       └── labels/
└── README.md        # This file
```

## Full Dataset

The model is trained on the **Francesco/furniture-ngpea** dataset from Hugging Face.

### Download Instructions

1. **Using Hugging Face Hub (Recommended)**:
   ```python
   from datasets import load_dataset
   dataset = load_dataset("Francesco/furniture-ngpea")
   ```

2. **Direct Download**:
   Visit: https://huggingface.co/datasets/Francesco/furniture-ngpea

3. **Using Training Script**:
   ```bash
   cd backend
   python train_francesco_furniture.py --download-only
   ```

### Dataset Statistics

- **Total Images**: ~900
- **Classes**: 4 (Furniture, Chair, Sofa, Table)
- **Format**: YOLO (bounding box annotations)

## Sample Dataset

The `sample/` directory contains a small subset (10-20 images) for:
- Quick testing and validation
- CI/CD pipeline tests
- Demo purposes

This sample is tracked in git and included in the repository.

## Training

To train the model on the full dataset:

```bash
cd backend
python train_francesco_furniture.py
```

Training configuration is in the script. Default settings:
- Model: YOLOv8n/YOLOv8m
- Epochs: 15
- Image Size: 640x640
- Batch Size: 8

## Model Weights

Trained model weights are saved to:
- `sytescan_training/models/` - Best and last checkpoints
- `backend/yolov8n.pt` - Default nano model

The production model achieves:
- **mAP50**: 0.995
- **Precision**: 0.993
- **Recall**: 0.999
