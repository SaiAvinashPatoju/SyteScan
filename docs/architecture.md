# SyteScan Architecture

This document describes the system architecture of SyteScan Progress Analyzer.

## Overview

SyteScan is a full-stack application with three main components:

1. **Frontend** - Next.js React application
2. **Backend** - FastAPI Python server
3. **ML Engine** - YOLOv8 object detection

## System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Browser                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Next.js Frontend (:3000)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Pages     │  │ Components  │  │   API Client (fetch)    │  │
│  │  - Dashboard│  │  - Upload   │  │                         │  │
│  │  - Projects │  │  - Charts   │  │                         │  │
│  │  - Analysis │  │  - Progress │  │                         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼ HTTP/REST
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (:8000)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  API Routes │  │  Services   │  │   Database (SQLAlchemy) │  │
│  │  - /api/*   │  │  - Project  │  │                         │  │
│  │  - /upload  │  │  - Upload   │  │                         │  │
│  │  - /health  │  │  - Progress │  │                         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│                         │                        │               │
│                         ▼                        ▼               │
│  ┌─────────────────────────────────┐  ┌───────────────────────┐ │
│  │     Detection Service           │  │    SQLite / PostgreSQL│ │
│  │  ┌───────────────────────────┐  │  │                       │ │
│  │  │   YOLOv8 Model            │  │  │  - Projects           │ │
│  │  │   (ultralytics)           │  │  │  - Images             │ │
│  │  │                           │  │  │  - Detections         │ │
│  │  └───────────────────────────┘  │  │  - Progress           │ │
│  └─────────────────────────────────┘  └───────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        File System                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   uploads/  │  │   models/   │  │      logs/              │  │
│  │  - images   │  │  - yolov8   │  │                         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (Next.js 14)

- **Framework**: Next.js 14 with App Router
- **UI Library**: React 18
- **Styling**: TailwindCSS
- **State Management**: React hooks
- **Forms**: react-hook-form
- **Charts**: Recharts

**Key Pages:**
- `/` - Landing/Dashboard
- `/projects` - Project listing
- `/projects/[id]` - Project details
- `/upload` - Image upload

### Backend (FastAPI)

- **Framework**: FastAPI 0.104
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic 2.5
- **ML**: Ultralytics YOLOv8

**API Endpoints:**
- `GET /health` - Health check
- `GET /api/projects` - List projects
- `POST /api/projects` - Create project
- `POST /api/upload` - Upload image
- `GET /api/progress/{id}` - Get progress

### ML Engine (YOLOv8)

- **Model**: YOLOv8n (nano) / YOLOv8m (medium)
- **Training Dataset**: Francesco/furniture-ngpea
- **Input**: 640x640 images
- **Output**: Bounding boxes with class labels

**Detection Classes:**
- Furniture (general)
- Chair
- Sofa
- Table

## Data Flow

1. **Image Upload**
   ```
   Browser → Frontend → Backend API → File Storage
   ```

2. **Detection**
   ```
   Backend → Load Image → YOLOv8 → Bounding Boxes → Database
   ```

3. **Progress Calculation**
   ```
   Detection Results → Progress Service → Percentage → Frontend
   ```

## Database Schema

```sql
-- Projects
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Images
CREATE TABLE images (
    id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    filename TEXT,
    filepath TEXT,
    uploaded_at TIMESTAMP
);

-- Detections
CREATE TABLE detections (
    id INTEGER PRIMARY KEY,
    image_id INTEGER REFERENCES images(id),
    class_name TEXT,
    confidence FLOAT,
    bbox_x FLOAT,
    bbox_y FLOAT,
    bbox_w FLOAT,
    bbox_h FLOAT
);
```

## Deployment Architecture

### Development
```
localhost:3000 (Frontend) ─────▶ localhost:8000 (Backend)
```

### Production (Docker)
```
nginx (reverse proxy)
    ├── :3000 → frontend container
    └── :8000 → backend container
                    └── volume: uploads/
                    └── volume: database
```

### Cloud (Render/Vercel)
```
Vercel (Frontend) ─────▶ Render (Backend + DB)
```

## Security Considerations

- File upload validation (type, size)
- CORS configuration
- Environment-based secrets
- Input validation (Pydantic)
- SQL injection prevention (SQLAlchemy ORM)

## Performance

- **Image Processing**: 2-10 seconds per image (CPU)
- **Model Size**: ~6MB (YOLOv8n)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Concurrency**: Multiple workers with uvicorn
