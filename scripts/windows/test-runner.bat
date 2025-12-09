@echo off
REM ==================================
REM SyteScan Test Runner
REM ==================================
REM Purpose: Run frontend and backend tests
REM Usage: Run from project root directory
REM ==================================

echo Running SyteScan Tests...
echo.

echo ================================
echo Frontend Tests (Vitest)
echo ================================
call npm test
if %errorlevel% neq 0 (
    echo Frontend tests failed!
) else (
    echo Frontend tests passed!
)

echo.
echo ================================
echo Backend Tests (Pytest)
echo ================================
cd backend
call venv\Scripts\pytest.exe -v
if %errorlevel% neq 0 (
    echo Backend tests failed!
) else (
    echo Backend tests passed!
)
cd ..

echo.
echo ================================
echo Test run complete!
echo ================================
