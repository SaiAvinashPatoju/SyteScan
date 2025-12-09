@echo off
REM ==================================
REM SyteScan Development Setup Script
REM ==================================
REM Purpose: Install all dependencies for frontend and backend
REM Usage: Run from project root directory
REM Requirements: Node.js 18+, Python 3.11+
REM ==================================

echo Setting up SyteScan Progress Analyzer...

echo.
echo [1/4] Installing frontend dependencies...
call npm install
if %errorlevel% neq 0 (
    echo Error: Failed to install frontend dependencies
    exit /b 1
)

echo.
echo [2/4] Creating Python virtual environment...
cd backend
python -m venv venv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment
    exit /b 1
)

echo.
echo [3/4] Installing backend dependencies...
call venv\Scripts\pip.exe install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install backend dependencies
    exit /b 1
)

cd ..

echo.
echo [4/4] Creating environment file...
if not exist .env.local (
    copy .env.example .env.local
    echo Environment file created: .env.local
) else (
    echo Environment file already exists: .env.local
)

echo.
echo ================================
echo Setup complete!
echo ================================
echo.
echo Next steps:
echo 1. Review and update .env.local if needed
echo 2. Run 'scripts\windows\start-dev.bat' to start servers
echo 3. Or use 'make run' with WSL/Git Bash
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
