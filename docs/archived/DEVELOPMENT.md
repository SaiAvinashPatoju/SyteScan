# SyteScan Progress Analyzer - Development Setup (Archived)

> **Note:** This document has been archived. Please see [DEV-SETUP.md](../../DEV-SETUP.md) for the current setup guide.

---

*Original content preserved below for reference:*

---

This document provides instructions for setting up the SyteScan Progress Analyzer for local development.

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd sytescan-progress-analyzer
```

### 2. Environment Setup

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` file with your local configuration if needed.

### 3. Backend Setup

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
mkdir -p uploads/projects
python main.py
```

### 4. Frontend Setup

```bash
npm install
npm run dev
```

## Testing

- Frontend: `npm test`
- Backend: `cd backend && pytest`

---

*Archived: December 2024*
