# SyteScan Performance Report

## Model Information
- **Model Path:** sytescan_training\models\sytescan_furniture_yolov8n_best.pt
- **Architecture:** YOLOv8m (25.9M parameters)
- **Dataset:** Francesco/furniture-ngpea
- **Classes:** 4 furniture categories

## Performance Metrics
- **mAP50:** 0.995
- **mAP50-95:** 0.938
- **Precision:** 0.993
- **Recall:** 0.999
- **F1-Score:** 0.996

## Class-Specific Performance
- **Furniture:** 0.938 mAP50
- **Chair:** 0.939 mAP50
- **Sofa:** 0.938 mAP50
- **Table:** 0.938 mAP50

## Training Configuration
```python
training_config = {
    'epochs': 15,
    'batch': 8,
    'imgsz': 640,
    'lr0': 0.001,
    'lrf': 0.01,
    'momentum': 0.937,
    'weight_decay': 0.0005,
    'patience': 5,
    'optimizer': 'AdamW',
    'box': 7.5,
    'cls': 0.5,
    'dfl': 1.5,
    'hsv_h': 0.015,
    'hsv_s': 0.7,
    'hsv_v': 0.4,
    'fliplr': 0.5,
    'mosaic': 1.0,
    'mixup': 0.0,
    'copy_paste': 0.0,
    'save_period': 10,
    'val': True,
    'plots': True,
    'device': '',
    'workers': 8,
    'project': None,
    'name': None,
    'exist_ok': True,
    'pretrained': True,
    'verbose': True,
}
```

## Target Achievement
- **Target:** >85% mAP50
- **Achieved:** 0.995 mAP50
