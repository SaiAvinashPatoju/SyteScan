@echo off
echo ========================================
echo SyteScan Progress Analyzer Training
echo Deep Learning Techniques Mini Project
echo Team: Shashank Ananth Iyer, Sai Avinash Patoju
echo ========================================
echo.

echo Installing required dependencies...
pip install -r requirements_final.txt

echo.
echo Starting SyteScan training pipeline...
echo This will download the Francesco dataset and train the YOLOv8m model.
echo Target: Achieve >85% mAP50 (Project achieved: 87.1% mAP50)
echo.

python final_sytescan_training_script.py --model-size m

echo.
echo Training completed! Check the sytescan_training folder for results.
echo.
pause