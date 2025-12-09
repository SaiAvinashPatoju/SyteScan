@echo off
echo Running SyteScan Progress Analyzer Tests...

echo.
echo [1/3] Running frontend tests...
call npm test
if %errorlevel% neq 0 (
    echo ❌ Frontend tests failed
    set "test_failed=1"
) else (
    echo ✅ Frontend tests passed
)

echo.
echo [2/3] Running backend tests...
cd backend
call venv\Scripts\pytest.exe -v
if %errorlevel% neq 0 (
    echo ❌ Backend tests failed
    set "test_failed=1"
) else (
    echo ✅ Backend tests passed
)

cd ..

echo.
echo [3/3] Running E2E tests...
call npm run test:e2e
if %errorlevel% neq 0 (
    echo ❌ E2E tests failed
    set "test_failed=1"
) else (
    echo ✅ E2E tests passed
)

echo.
if defined test_failed (
    echo ❌ Some tests failed. Check the output above for details.
    exit /b 1
) else (
    echo ✅ All tests passed!
)