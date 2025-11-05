# 🪑 Furniture Detection System

**AI-powered furniture detection using fine-tuned YOLOv8x model**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/deploy)

## 🎯 Project Overview

This system uses a fine-tuned YOLOv8x model to detect furniture in construction and interior images, achieving **89.6% mAP@0.5 accuracy**. Built as part of a Deep Learning Techniques project for construction progress monitoring and interior design verification.

## 📊 Model Performance

| Metric | Pre-trained | Fine-tuned | Improvement |
|--------|-------------|------------|-------------|
| mAP@0.5 | 58.2% | **89.6%** | +31.4% |
| mAP@0.5:0.95 | 35.4% | **69.6%** | +34.2% |
| Precision | 72.1% | **95.3%** | +23.2% |
| Recall | 65.3% | **94.7%** | +29.4% |

## 🚀 Quick Deploy

### Option 1: Railway (Recommended)
1. Click the "Deploy on Railway" button above
2. Connect your GitHub account
3. Deploy automatically! 🎉

### Option 2: Manual Deployment
```bash
# Clone repository
git clone <your-repo-url>
cd furniture-detection

# Build and run with Docker
docker build -t furniture-detection .
docker run -p 8000:8000 furniture-detection
```

## 🛠️ Local Development

### Prerequisites
- Python 3.9+
- Docker (optional)

### Setup
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run backend
cd backend
python main_production.py

# Access at http://localhost:8000
```

## 📁 Project Structure

```
furniture-detection/
├── backend/                    # FastAPI backend
│   ├── app/                   # Application modules
│   ├── main_production.py     # Production server
│   ├── furniture_yolov8x_demo.pt  # Fine-tuned model
│   └── requirements.txt       # Python dependencies
├── frontend/                  # Web interface
│   ├── index.html            # Main page
│   ├── script.js             # Frontend logic
│   └── style.css             # Styling
├── runs/                     # Training results
├── ProgressAnalyzerDLTminiSubmissions/  # Project submissions
├── Dockerfile               # Container configuration
├── railway.json            # Railway deployment config
└── PROJECT_REPORT.md       # Detailed project report
```

## 🎯 Features

- **🖼️ Image Upload**: Drag-and-drop or click to upload
- **🎯 Real-time Detection**: Furniture detection with bounding boxes
- **📊 Confidence Scores**: Percentage confidence for each detection
- **📱 Responsive Design**: Works on desktop and mobile
- **⚡ Fast Processing**: Results in 2-3 seconds
- **🔒 Secure**: HTTPS encryption and secure file handling

## 🧠 Technical Details

### Model Architecture
- **Base Model**: YOLOv8x (68.2M parameters)
- **Training Dataset**: Francesco/furniture-ngpea
- **Classes**: Chair, Sofa, Table, Furniture
- **Training**: 50 epochs with early stopping
- **Optimizer**: AdamW with cosine learning rate scheduling

### Technology Stack
- **Backend**: FastAPI, Python 3.9+
- **Frontend**: HTML5, JavaScript, CSS3
- **ML Framework**: Ultralytics YOLOv8
- **Deployment**: Docker, Railway
- **Model**: PyTorch

## 📈 Use Cases

- **Construction Progress Monitoring**: Track furniture installation progress
- **Interior Design Verification**: Validate design implementations
- **Space Utilization Analysis**: Analyze furniture placement and usage
- **Quality Control**: Automated inspection of furnished spaces
- **Real Estate**: Property inventory and documentation

## 🔧 API Endpoints

- `GET /` - Web interface
- `POST /api/upload/detect` - Furniture detection
- `GET /api/health` - Health check
- `GET /api/model-info` - Model information

## 📊 Training Results

The model was trained for 50 epochs with the following configuration:
- **Batch Size**: 8
- **Image Size**: 640x640
- **Optimizer**: AdamW (lr=0.001)
- **Data Augmentation**: Mosaic, horizontal flip, HSV adjustments
- **Early Stopping**: Patience of 10 epochs

Training curves and detailed results available in `runs/furniture/yolov8x_furniture_demo/`

## 🎓 Academic Project

This project was developed as part of a **Deep Learning Techniques** course, demonstrating:
- Complete ML pipeline from data analysis to deployment
- Production-ready system architecture
- High-performance model optimization
- Real-world application development

## 📄 License

This project is developed for academic purposes as part of a Deep Learning Techniques course.

## 👥 Contributors

**Deep Learning Techniques Project Team**
- Furniture Detection for Construction Progress Monitoring
- Fine-tuned YOLOv8x achieving 89.6% mAP@0.5

---

**🎯 Live Demo**: [Your Railway URL will appear here after deployment]