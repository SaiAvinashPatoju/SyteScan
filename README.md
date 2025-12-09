# SyteScan - Progress Analyzer

SyteScan is a comprehensive construction progress monitoring solution that uses computer vision to analyze site photos and track project completion.

## Project Structure

The project is organized into the following components:

- **`frontend/`**: Next.js application for the user interface.
- **`backend/`**: Python FastAPI backend for image processing and data management.
- **`ml/`**: Machine Learning resources (YOLO models, training data, runs).
- **`scripts/`**: Utility scripts for setup, testing, and deployment.
- **`docs/`**: Developer and deployment documentation.

## Getting Started

### Prerequisites

- Node.js (v18+)
- Python (v3.11+)
- Docker & Docker Compose (optional, for containerized run)

### Setup

1.  **Initialize the project:**
    ```bash
    .\scripts\setup.bat
    ```

2.  **Start Development Servers:**
    ```bash
    .\scripts\start-dev.bat
    ```
    This will start both the frontend (localhost:3000) and backend (localhost:8000).

## Docker Deployment

To run the full stack using Docker:

```bash
docker-compose up --build
```

Ensure you have updated your `docker-compose.yml` to reflect the new `frontend/` and `backend/` build contexts.

## Documentation

- [Development Guide](docs/DEVELOPMENT.md): Code standards and workflow.
- [Setup Guide](docs/DEV-SETUP.md): Detailed installation instructions.
- [Deployment](docs/DEPLOYMENT.md): Production deployment steps.
