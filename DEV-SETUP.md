# SyteScan Progress Analyzer - Development Setup Guide

## Quick Start

### 1. Automated Setup
Run the setup script to install all dependencies:
```bash
setup.bat
```

### 2. Start Development Servers
```bash
start-dev.bat
```

This will start both frontend (port 3000) and backend (port 8000) servers.

### 3. Run Tests
```bash
run-tests.bat
```

## VS Code Integration

### Debug Configurations
- **Debug Full Stack**: Starts both frontend and backend in debug mode
- **Debug Frontend (Next.js)**: Debug the Next.js frontend only
- **Debug Backend (FastAPI)**: Debug the FastAPI backend only
- **Debug Tests**: Debug frontend or backend tests

### Tasks Available
- **Setup: Complete Project Setup**: Full automated setup
- **Run: Frontend Development**: Start frontend dev server
- **Run: Backend Development**: Start backend dev server
- **Test: Frontend/Backend**: Run tests
- **Build: Frontend Production**: Build for production
- **Docker: Build and Run**: Run with Docker

### Keyboard Shortcuts
- `Ctrl+Shift+P` → "Tasks: Run Task" to access all tasks
- `F5` → Start debugging (select configuration)
- `Ctrl+F5` → Run without debugging

## Manual Setup (if needed)

### Prerequisites
- Node.js 18+
- Python 3.11+
- Git

### Frontend Setup
```bash
npm install
npm run dev  # Starts on http://localhost:3000
```

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py  # Starts on http://localhost:8000
```

## Development Workflow

### 1. Environment Configuration
- Copy `.env.example` to `.env.local`
- Modify environment variables as needed
- Backend uses SQLite by default (no additional setup required)

### 2. File Structure
```
├── src/                 # Frontend (Next.js)
├── backend/            # Backend (FastAPI)
│   ├── app/           # Application code
│   ├── tests/         # Backend tests
│   └── venv/          # Python virtual environment
├── .vscode/           # VS Code configuration
└── uploads/           # File storage
```

### 3. API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 4. Testing
- **Frontend**: `npm test` (Vitest)
- **Backend**: `cd backend && venv\Scripts\pytest.exe`
- **E2E**: `npm run test:e2e`

### 5. Linting & Code Quality
- **Frontend**: `npm run lint`
- **Backend**: Configure flake8/black in VS Code

## Debugging Tips

### Frontend Debugging
- Use VS Code debugger with "Debug Frontend" configuration
- React DevTools browser extension recommended
- Check browser console for client-side errors

### Backend Debugging
- Use VS Code debugger with "Debug Backend" configuration
- Set breakpoints in Python code
- Check terminal output for server logs
- Use `/health` endpoint to verify backend is running

### Common Issues
1. **Port conflicts**: Change ports in configuration files
2. **Python path issues**: Ensure virtual environment is activated
3. **CORS errors**: Check CORS_ORIGINS in environment variables
4. **File upload issues**: Verify uploads directory permissions

## Production Build

### Local Production Build
```bash
npm run build
npm start
```

### Docker Production
```bash
docker-compose up --build
```

## Performance Notes
- YOLOv8 model downloads automatically on first run (~6MB)
- Image processing takes 2-10 seconds depending on hardware
- SQLite database created automatically in backend directory

## Useful URLs
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health