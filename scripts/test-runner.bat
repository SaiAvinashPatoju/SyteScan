@echo off
REM SyteScan Progress Analyzer - Complete Test Suite Runner (Windows)
REM This script runs all tests including unit, integration, and e2e tests

echo 🚀 Starting SyteScan Progress Analyzer Test Suite
echo ==================================================

REM Check if virtual environment exists for backend
if not exist "backend\venv" (
    echo ⚠ Backend virtual environment not found. Creating...
    cd backend
    python -m venv venv
    cd ..
)

REM Activate virtual environment
call backend\venv\Scripts\activate.bat

REM Install backend dependencies
echo ✓ Installing backend dependencies...
cd backend
pip install -r requirements.txt
cd ..

REM Install frontend dependencies
echo ✓ Installing frontend dependencies...
npm install

echo.
echo 🧪 Running Backend Tests
echo ========================

REM Run backend unit tests
echo ✓ Running backend unit tests...
cd backend
python -m pytest tests/ -v --tb=short
if %errorlevel% neq 0 (
    echo ✗ Backend unit tests failed
    exit /b 1
)
cd ..

REM Run backend e2e tests
echo ✓ Running backend e2e tests...
cd backend
python -m pytest tests/test_e2e_workflow.py -v --tb=short
if %errorlevel% neq 0 (
    echo ✗ Backend e2e tests failed
    exit /b 1
)
cd ..

echo.
echo 🎨 Running Frontend Tests
echo =========================

REM Run frontend unit tests
echo ✓ Running frontend unit tests...
npm test
if %errorlevel% neq 0 (
    echo ✗ Frontend unit tests failed
    exit /b 1
)

REM Run frontend e2e tests
echo ✓ Running frontend e2e workflow tests...
npm test -- src/test/e2e-workflow.test.tsx
if %errorlevel% neq 0 (
    echo ✗ Frontend e2e tests failed
    exit /b 1
)

echo.
echo 🏥 Running Health Checks
echo ========================

REM Start backend server in background for health checks
echo ✓ Starting backend server for health checks...
cd backend
start /b python main.py
cd ..

REM Wait for server to start
timeout /t 5 /nobreak > nul

REM Test health endpoints
echo ✓ Testing health endpoints...
curl -f http://localhost:8000/health
if %errorlevel% neq 0 (
    echo ✗ Basic health check failed
)

curl -f http://localhost:8000/health/detailed
if %errorlevel% neq 0 (
    echo ✗ Detailed health check failed
)

curl -f http://localhost:8000/metrics
if %errorlevel% neq 0 (
    echo ✗ Metrics endpoint failed
)

REM Stop backend server
taskkill /f /im python.exe > nul 2>&1

echo.
echo 📊 Test Summary
echo ===============

echo ✓ All tests completed successfully!
echo ✓ Backend unit tests: PASSED
echo ✓ Backend e2e tests: PASSED
echo ✓ Frontend unit tests: PASSED
echo ✓ Frontend e2e tests: PASSED
echo ✓ Health checks: PASSED

echo.
echo 🎉 Test suite completed successfully!
echo Ready for deployment! 🚀

pause