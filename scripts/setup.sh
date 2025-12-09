#!/bin/bash
# ==================================
# SyteScan Development Setup Script
# ==================================
# Purpose: Install all dependencies for frontend and backend
# Usage: ./scripts/setup.sh
# Requirements: Node.js 18+, Python 3.11+
# ==================================

set -e

echo "Setting up SyteScan Progress Analyzer..."
echo

echo "[1/4] Installing frontend dependencies..."
npm install

echo
echo "[2/4] Creating Python virtual environment..."
cd backend
python3 -m venv venv

echo
echo "[3/4] Installing backend dependencies..."
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

echo
echo "[4/4] Creating environment file..."
if [ ! -f .env.local ]; then
    cp .env.example .env.local
    echo "Environment file created: .env.local"
else
    echo "Environment file already exists: .env.local"
fi

echo
echo "================================"
echo "✅ Setup complete!"
echo "================================"
echo
echo "Next steps:"
echo "1. Review and update .env.local if needed"
echo "2. Run 'make run' to start development servers"
echo
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
