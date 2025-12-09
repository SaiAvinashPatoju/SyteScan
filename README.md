# SyteScan Progress Analyzer

AI-powered construction progress tracking platform that compares architectural blueprints against actual implementation through room images.

## Project Structure

```
├── src/                    # Next.js frontend
│   ├── app/               # App router pages
│   ├── components/        # React components
│   └── test/             # Frontend tests
├── backend/               # FastAPI backend
│   ├── app/              # Application code
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── database/     # Database utilities
│   └── tests/            # Backend tests
└── uploads/              # File storage
```

## Development Setup

### Frontend (Next.js)

```bash
npm install
npm run dev
```

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Testing

### Frontend Tests

```bash
npm test
```

### Backend Tests

```bash
cd backend
pytest
```

## Technology Stack

- **Frontend**: Next.js 14, TypeScript, TailwindCSS, React Hook Form, Recharts
- **Backend**: FastAPI, SQLAlchemy, Pydantic, YOLOv8
- **Database**: SQLite (development), PostgreSQL (production)
- **AI**: Ultralytics YOLOv8 for object detection
