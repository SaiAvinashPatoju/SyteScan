# SyteScan Progress Analyzer - Development Setup

This document provides instructions for setting up the SyteScan Progress Analyzer for local development.

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd sytescan-progress-analyzer
```

### 2. Environment Setup

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` file with your local configuration if needed.

### 3. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create uploads directory
mkdir -p uploads/projects

# Start the backend server
python main.py
```

The backend API will be available at `http://localhost:8000`

### 4. Frontend Setup

Open a new terminal window:

```bash
# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Development Workflow

### Running Tests

**Backend Tests:**
```bash
cd backend
pytest
```

**Frontend Tests:**
```bash
npm test
```

### Code Quality

**Backend Linting:**
```bash
cd backend
flake8 app/
black app/
```

**Frontend Linting:**
```bash
npm run lint
```

### Database Management

The application uses SQLite by default. The database file (`sytescan.db`) will be created automatically in the backend directory.

To reset the database:
```bash
cd backend
rm sytescan.db
python main.py  # Will recreate tables on startup
```

### File Uploads

Uploaded files are stored in `backend/uploads/projects/{project_id}/` directory structure.

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Troubleshooting

### Common Issues

1. **YOLOv8 Model Download Issues:**
   - The first run will download the YOLOv8 nano model (~6MB)
   - Ensure you have internet connection during first startup

2. **Port Conflicts:**
   - Frontend default: 3000
   - Backend default: 8000
   - Change ports in respective configuration files if needed

3. **Python Virtual Environment:**
   - Always activate the virtual environment before running backend commands
   - Use `deactivate` to exit the virtual environment

4. **File Upload Permissions:**
   - Ensure the `uploads` directory has write permissions
   - On Unix systems: `chmod 755 uploads`

### Performance Notes

- YOLOv8 runs on CPU by default for compatibility
- Image processing may take 2-10 seconds per image depending on hardware
- For faster processing, ensure you have a modern CPU with multiple cores

## Production Deployment

For production deployment options, see the Docker files:
- `Dockerfile.frontend` - Frontend production build
- `Dockerfile.backend` - Backend production build
- `docker-compose.yml` - Complete stack deployment

### Docker Development

To run the entire stack with Docker:

```bash
docker-compose up --build
```

This will start both frontend and backend services with production configurations.

## Project Structure

```
sytescan-progress-analyzer/
├── src/                    # Next.js frontend source
│   ├── app/               # App router pages
│   ├── components/        # React components
│   ├── lib/              # Utility functions
│   └── types/            # TypeScript types
├── backend/               # FastAPI backend
│   ├── app/              # Application code
│   │   ├── api/          # API routes
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   └── database/     # Database utilities
│   └── tests/            # Backend tests
├── uploads/              # File storage
└── .kiro/               # Kiro specifications
```

## Contributing

1. Create a feature branch from main
2. Make your changes
3. Run tests to ensure everything works
4. Submit a pull request

For more detailed information about the project architecture and requirements, see the specification documents in `.kiro/specs/sytescan-progress-analyzer/`.