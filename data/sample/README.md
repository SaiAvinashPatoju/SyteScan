# Sample Dataset

This directory contains a small sample of the training dataset for testing purposes.

## Purpose

- Quick validation of model loading and inference
- CI/CD pipeline testing
- Demo and development testing

## Contents

Place sample images and labels here:
- `images/` - JPEG/PNG images
- `labels/` - YOLO format label files (.txt)

## Dataset Format

Labels use YOLO format:
```
<class_id> <x_center> <y_center> <width> <height>
```

All values are normalized (0-1) relative to image dimensions.

## Classes

| ID | Class |
|----|-------|
| 0  | Furniture |
| 1  | Chair |
| 2  | Sofa |
| 3  | Table |
