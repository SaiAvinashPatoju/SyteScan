# ==================================
# SyteScan Progress Analyzer Makefile
# ==================================
# Use: make <target>
# Run `make help` to see all available targets

.PHONY: help setup setup-frontend setup-backend build run test lint clean deploy-local docker-build docker-up docker-down

# Default target
.DEFAULT_GOAL := help

# ============ Help ============
help: ## Show this help message
	@echo "SyteScan Progress Analyzer - Development Tasks"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ============ Setup ============
setup: setup-frontend setup-backend ## Complete project setup (frontend + backend)
	@echo "✅ Setup complete!"

setup-frontend: ## Install frontend dependencies
	@echo "📦 Installing frontend dependencies..."
	npm install

setup-backend: ## Set up backend Python environment
	@echo "🐍 Setting up backend..."
	cd backend && python -m venv venv
	cd backend && venv/bin/pip install -r requirements.txt || venv\Scripts\pip.exe install -r requirements.txt
	@echo "✅ Backend setup complete"

# ============ Build ============
build: build-frontend ## Build for production
	@echo "✅ Build complete!"

build-frontend: ## Build frontend for production
	@echo "🔨 Building frontend..."
	npm run build

# ============ Run ============
run: ## Start development servers (frontend + backend)
	@echo "🚀 Starting development servers..."
	@echo "Frontend: http://localhost:3000"
	@echo "Backend:  http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo ""
	@echo "Run frontend and backend in separate terminals:"
	@echo "  Terminal 1: make run-frontend"
	@echo "  Terminal 2: make run-backend"

run-frontend: ## Start frontend dev server
	npm run dev

run-backend: ## Start backend dev server
	cd backend && venv/bin/python main.py || venv\Scripts\python.exe main.py

# ============ Test ============
test: test-frontend test-backend ## Run all tests
	@echo "✅ All tests complete!"

test-frontend: ## Run frontend tests
	@echo "🧪 Running frontend tests..."
	npm test

test-backend: ## Run backend tests
	@echo "🧪 Running backend tests..."
	cd backend && venv/bin/pytest || venv\Scripts\pytest.exe

test-e2e: ## Run end-to-end tests
	npm run test:e2e

# ============ Lint ============
lint: lint-frontend lint-backend ## Run all linters
	@echo "✅ Linting complete!"

lint-frontend: ## Lint frontend code
	@echo "🔍 Linting frontend..."
	npm run lint

lint-backend: ## Lint backend code
	@echo "🔍 Linting backend..."
	cd backend && venv/bin/flake8 app/ || venv\Scripts\flake8.exe app/

# ============ Clean ============
clean: ## Remove build artifacts and caches
	@echo "🧹 Cleaning..."
	rm -rf .next
	rm -rf node_modules/.cache
	rm -rf coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Clean complete!"

clean-all: clean ## Remove all generated files including node_modules and venv
	rm -rf node_modules
	rm -rf backend/venv
	rm -rf .venv
	@echo "✅ Full clean complete!"

# ============ Docker ============
docker-build: ## Build Docker images
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-up: ## Start Docker containers
	@echo "🐳 Starting Docker containers..."
	docker-compose up -d
	@echo "Frontend: http://localhost:3000"
	@echo "Backend:  http://localhost:8000"

docker-down: ## Stop Docker containers
	@echo "🐳 Stopping Docker containers..."
	docker-compose down

docker-logs: ## View Docker container logs
	docker-compose logs -f

deploy-local: docker-build docker-up ## Deploy locally using Docker
	@echo "✅ Local deployment complete!"

# ============ Database ============
db-reset: ## Reset the database
	@echo "🗄️  Resetting database..."
	rm -f backend/sytescan.db
	@echo "✅ Database reset. Will be recreated on next backend start."

# ============ Utility ============
check-deps: ## Check for outdated dependencies
	@echo "📦 Checking frontend dependencies..."
	npm outdated || true
	@echo ""
	@echo "🐍 Checking backend dependencies..."
	cd backend && venv/bin/pip list --outdated || venv\Scripts\pip.exe list --outdated

health: ## Check health of running services
	@echo "🏥 Checking service health..."
	@curl -s http://localhost:8000/health && echo " - Backend OK" || echo " - Backend not running"
	@curl -s http://localhost:3000 > /dev/null && echo " - Frontend OK" || echo " - Frontend not running"
