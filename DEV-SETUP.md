# SyteScan Progress Analyzer - Development Setup

Complete guide for setting up the SyteScan development environment.

## Prerequisites

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| Node.js | 18+ | `node --version` |
| Python | 3.11+ | `python --version` |
| Git | Latest | `git --version` |
| Docker | Optional | `docker --version` |

## Quick Start

### Option 1: Automated Setup (Recommended)

**Windows:**
```bash
scripts\windows\setup.bat
scripts\windows\start-dev.bat
```

**macOS/Linux:**
```bash
chmod +x scripts/*.sh
./scripts/setup.sh
make run-frontend  # Terminal 1
make run-backend   # Terminal 2
```

### Option 2: Make (Unix/WSL)

```bash
make setup    # Install all dependencies
make run      # Show run instructions
```

### Option 3: Docker

```bash
docker-compose up --build
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
```

---

## Manual Setup

### 1. Clone & Configure

```bash
git clone <repository-url>
cd sytescan

# Create environment file
cp .env.example .env.local
```

### 2. Frontend Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
# → http://localhost:3000
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (choose your OS)
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server
python main.py
# → http://localhost:8000
```

---

## Project Structure

```
sytescan/
├── src/                    # Next.js frontend
│   ├── app/               # App router pages
│   ├── components/        # React components
│   ├── lib/               # Utilities
│   └── types/             # TypeScript types
├── backend/               # FastAPI backend
│   ├── app/               # Application code
│   │   ├── api/          # API routes
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   └── database/     # DB utilities
│   └── tests/            # Backend tests
├── scripts/               # Helper scripts
│   └── windows/          # Windows batch files
├── data/                  # Training datasets
│   └── sample/           # Small test dataset
├── docs/                  # Documentation
└── uploads/              # Runtime file storage
```

---

## Development Workflow

### Running Tests

```bash
# All tests
make test

# Frontend only
npm test

# Backend only
cd backend && pytest

# End-to-end
npm run test:e2e
```

### Linting

```bash
# Frontend (ESLint)
npm run lint

# Backend (flake8)
cd backend && flake8 app/
```

### Database

SQLite is used by default. The database file (`sytescan.db`) is created automatically.

**Reset database:**
```bash
rm backend/sytescan.db
# Restart backend to recreate
```

---

## API Documentation

Once the backend is running:

| URL | Description |
|-----|-------------|
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc |
| http://localhost:8000/health | Health check |

---

## VS Code Integration

### Debug Configurations

The project includes VS Code configurations for debugging:

- **Debug Full Stack** - Both frontend and backend
- **Debug Frontend (Next.js)** - Frontend only
- **Debug Backend (FastAPI)** - Backend only

### Tasks

Access via `Ctrl+Shift+P` → "Tasks: Run Task":

- Setup: Complete Project Setup
- Run: Frontend/Backend Development
- Test: Frontend/Backend
- Build: Frontend Production
- Docker: Build and Run

---

## Environment Variables

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (environment or .env)

```bash
DATABASE_URL=sqlite:///./sytescan.db
UPLOAD_DIR=./uploads
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000
```

---

## Troubleshooting

### Port Conflicts

Default ports:
- Frontend: 3000
- Backend: 8000

Change in respective config files if needed.

### Python Virtual Environment

Always activate before running backend:
```bash
# Windows
backend\venv\Scripts\activate

# macOS/Linux
source backend/venv/bin/activate
```

### YOLOv8 Model

The model downloads automatically on first run (~6MB). Ensure internet connectivity.

### File Upload Issues

Verify `uploads/` directory exists with write permissions:
```bash
mkdir -p uploads/projects
chmod 755 uploads  # Unix only
```

### CORS Errors

Check `CORS_ORIGINS` environment variable matches your frontend URL.

---

## Performance Notes

- **Image Processing**: 2-10 seconds per image (CPU)
- **Model Size**: ~6MB (YOLOv8n)
- **First Run**: Model download required

For production deployment, see [DEPLOYMENT.md](DEPLOYMENT.md).