# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Repository restructuring for production-grade organization
- Comprehensive .gitignore for Python, Node.js, and datasets
- CONTRIBUTING.md with contribution guidelines
- CODE_OF_CONDUCT.md (Contributor Covenant v2.0)
- SECURITY.md with vulnerability reporting instructions
- GitHub Actions CI workflow for automated testing
- Makefile with common development tasks
- Consolidated documentation in `docs/` directory
- `scripts/` directory for organized helper scripts

### Changed
- Reorganized project structure for clarity
- Updated README.md with production-ready documentation
- Consolidated DEV-SETUP.md and DEVELOPMENT.md
- Moved Windows batch scripts to `scripts/windows/`

### Removed
- Python bytecode files (__pycache__, *.pyc)
- Duplicate documentation files

## [0.1.0] - 2024-12-09

### Added
- Initial release of SyteScan Progress Analyzer
- YOLOv8-based construction progress detection
- Next.js frontend with React components
- FastAPI backend with SQLite database
- Project management functionality
- Image upload and analysis
- Progress tracking and visualization
- Docker deployment support
- Unit and integration tests

### Technical Details
- Frontend: Next.js 14, React 18, TailwindCSS
- Backend: FastAPI, SQLAlchemy, Pydantic
- ML Model: YOLOv8n trained on furniture dataset
- Database: SQLite (PostgreSQL ready)
