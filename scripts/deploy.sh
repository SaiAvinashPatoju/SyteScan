#!/bin/bash
# ==================================
# SyteScan Deployment Script
# ==================================
# Purpose: Deploy the application using Docker
# Usage: ./scripts/deploy.sh [environment]
# Environments: local, production
# ==================================

set -e

ENVIRONMENT=${1:-local}

echo "Deploying SyteScan ($ENVIRONMENT)..."
echo

case $ENVIRONMENT in
    local)
        echo "Building and starting Docker containers..."
        docker-compose down 2>/dev/null || true
        docker-compose up --build -d
        
        echo
        echo "Waiting for services to start..."
        sleep 5
        
        echo
        echo "Checking health..."
        curl -s http://localhost:8000/health && echo " - Backend OK" || echo " - Backend starting..."
        curl -s http://localhost:3000 > /dev/null && echo " - Frontend OK" || echo " - Frontend starting..."
        
        echo
        echo "================================"
        echo "✅ Local deployment complete!"
        echo "================================"
        echo "Frontend: http://localhost:3000"
        echo "Backend:  http://localhost:8000"
        echo "API Docs: http://localhost:8000/docs"
        echo
        echo "View logs: docker-compose logs -f"
        echo "Stop:      docker-compose down"
        ;;
        
    production)
        echo "Production deployment..."
        echo
        echo "For production deployment, please:"
        echo "1. Set up your cloud provider (Render, Railway, or AWS)"
        echo "2. Configure environment variables"
        echo "3. Push to your deployment branch"
        echo
        echo "See DEPLOYMENT.md for detailed instructions."
        ;;
        
    *)
        echo "Unknown environment: $ENVIRONMENT"
        echo "Usage: ./scripts/deploy.sh [local|production]"
        exit 1
        ;;
esac
