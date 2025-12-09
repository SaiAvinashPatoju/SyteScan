@echo off
REM ==================================
REM SyteScan Development Server Launcher
REM ==================================
REM Purpose: Start both frontend and backend development servers
REM Usage: Run from project root directory
REM ==================================

echo Starting SyteScan Progress Analyzer in development mode...

echo.
echo Starting backend server...
start "Backend Server" cmd /k "cd backend && venv\Scripts\python.exe main.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo.
echo Starting frontend server...
start "Frontend Server" cmd /k "npm run dev"

echo.
echo ================================
echo Both servers are starting!
echo ================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to stop all servers...
pause > nul

echo.
echo Stopping servers...
taskkill /f /im "node.exe" 2>nul
taskkill /f /im "python.exe" 2>nul
echo Servers stopped.
