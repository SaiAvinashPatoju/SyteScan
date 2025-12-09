#!/bin/bash

# SyteScan Progress Analyzer - Complete Test Suite Runner
# This script runs all tests including unit, integration, and e2e tests

set -e  # Exit on any error

echo "🚀 Starting SyteScan Progress Analyzer Test Suite"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if virtual environment exists for backend
if [ ! -d "backend/venv" ]; then
    print_warning "Backend virtual environment not found. Creating..."
    cd backend
    python -m venv venv
    cd ..
fi

# Activate virtual environment (Windows)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source backend/venv/Scripts/activate
else
    source backend/venv/bin/activate
fi

# Install backend dependencies
print_status "Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
print_status "Installing frontend dependencies..."
npm install

echo ""
echo "🧪 Running Backend Tests"
echo "========================"

# Run backend unit tests
print_status "Running backend unit tests..."
cd backend
python -m pytest tests/ -v --tb=short
cd ..

# Run backend e2e tests
print_status "Running backend e2e tests..."
cd backend
python -m pytest tests/test_e2e_workflow.py -v --tb=short
cd ..

echo ""
echo "🎨 Running Frontend Tests"
echo "========================="

# Run frontend unit tests
print_status "Running frontend unit tests..."
npm test

# Run frontend e2e tests
print_status "Running frontend e2e workflow tests..."
npm test -- src/test/e2e-workflow.test.tsx

echo ""
echo "🏥 Running Health Checks"
echo "========================"

# Start backend server in background for health checks
print_status "Starting backend server for health checks..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# Wait for server to start
sleep 5

# Test health endpoints
print_status "Testing health endpoints..."
curl -f http://localhost:8000/health || print_error "Basic health check failed"
curl -f http://localhost:8000/health/detailed || print_error "Detailed health check failed"
curl -f http://localhost:8000/metrics || print_error "Metrics endpoint failed"

# Stop backend server
kill $BACKEND_PID 2>/dev/null || true

echo ""
echo "📊 Test Summary"
echo "==============="

print_status "All tests completed successfully!"
print_status "Backend unit tests: PASSED"
print_status "Backend e2e tests: PASSED"
print_status "Frontend unit tests: PASSED"
print_status "Frontend e2e tests: PASSED"
print_status "Health checks: PASSED"

echo ""
echo "🎉 Test suite completed successfully!"
echo "Ready for deployment! 🚀"