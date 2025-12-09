<div align="center">

# 🏗️ SyteScan Progress Analyzer

**AI-powered construction progress monitoring using computer vision**

[![CI](https://github.com/YOUR_USERNAME/sytescan/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/sytescan/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)

[Live Demo](#) • [Documentation](docs/) • [Quick Start](#-quick-start) • [API Docs](http://localhost:8000/docs)

</div>

---

## 🎯 Overview

SyteScan is a comprehensive construction progress monitoring solution that uses **YOLOv8** computer vision to analyze site photos and automatically track project completion. Upload images, detect construction elements, and visualize progress over time.

### Key Features

- 📸 **Image Upload & Analysis** - Drag-and-drop interface for site photos
- 🤖 **AI-Powered Detection** - YOLOv8 model trained for construction elements
- 📊 **Progress Tracking** - Automated progress calculation and visualization
- 📈 **Project Dashboard** - Visual timeline and progress charts
- 🐳 **Docker Ready** - One-command deployment with Docker Compose
- 🧪 **Fully Tested** - Comprehensive unit and integration tests

---

## 🚀 Quick Start

Get up and running in 3 commands:

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/sytescan.git && cd sytescan

# 2. Install dependencies
make setup

# 3. Start development servers
make run-frontend  # Terminal 1: http://localhost:3000
make run-backend   # Terminal 2: http://localhost:8000
```

Or use Docker:

```bash
docker-compose up --build
# Frontend: http://localhost:3000 | Backend: http://localhost:8000
```

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Next.js UI    │────▶│  FastAPI API    │────▶│   YOLOv8 ML     │
│   (React 18)    │     │  (Python 3.11)  │     │   (Detection)   │
│                 │     │                 │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │                 │
                        │    SQLite DB    │
                        │  (PostgreSQL    │
                        │   ready)        │
                        └─────────────────┘
```

For detailed architecture documentation, see [docs/architecture.md](docs/architecture.md).

---

## 📁 Project Structure

```
sytescan/
├── src/                    # Next.js frontend source
│   ├── app/               # App router pages
│   ├── components/        # React components
│   └── lib/               # Utilities
├── backend/               # FastAPI backend
│   ├── app/               # Application code
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Database models
│   │   └── services/     # Business logic
│   └── tests/            # Backend tests
├── scripts/               # Helper scripts
│   └── windows/          # Windows batch files
├── docs/                  # Documentation
│   └── archived/         # Historical docs
├── data/                  # Datasets (gitignored)
│   └── sample/           # Small demo dataset
├── uploads/               # Runtime file storage
├── Dockerfile.frontend    # Frontend Docker image
├── Dockerfile.backend     # Backend Docker image
└── docker-compose.yml     # Full stack orchestration
```

---

## 🧪 Running Tests

```bash
# All tests
make test

# Frontend only
make test-frontend

# Backend only
make test-backend

# End-to-end
make test-e2e
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [DEV-SETUP.md](DEV-SETUP.md) | Development environment setup |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Production deployment guide |
| [docs/architecture.md](docs/architecture.md) | System architecture |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

---

## 🐳 Docker Deployment

### Development

```bash
docker-compose up --build
```

### Production

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete production deployment instructions including:
- Environment configuration
- Nginx reverse proxy setup
- SSL/TLS configuration
- Database migration to PostgreSQL
- Monitoring and logging

---

## 📊 Dataset

The model is trained on the [Francesco/furniture-ngpea](https://huggingface.co/datasets/Francesco/furniture-ngpea) dataset.

**Performance:**
- mAP50: **0.995**
- Precision: **0.993**
- Recall: **0.999**

To use the full training dataset:
1. Download from the link above
2. Place in `data/francesco_training/`
3. Run training script: `python backend/train_francesco_furniture.py`

A small sample is included in `data/sample/` for testing.

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**Deep Learning Techniques Mini Project**

- Shashank Ananth Iyer
- Sai Avinash Patoju

---

<div align="center">

**[⬆ Back to Top](#-sytescan-progress-analyzer)**

Made with ❤️ for construction progress tracking

</div>
