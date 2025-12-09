@echo off
echo ========================================
echo Francesco Furniture Model Training
echo ========================================
echo.

cd backend

echo Installing required dependencies...
pip install datasets huggingface_hub

echo.
echo Starting Francesco furniture model training...
echo This will download the dataset and train a YOLOv8 model.
echo.

python train_francesco_furniture.py --model-size n --epochs 30

echo.
echo Training completed! Check the francesco_training folder for results.
echo.
pause