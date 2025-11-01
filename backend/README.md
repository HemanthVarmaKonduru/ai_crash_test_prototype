# Backend API Server

Modular backend API for Evalence AI Security Testing Platform.

## Structure

```
backend/
├── api/
│   └── main.py              # FastAPI application entry point
├── config/
│   └── settings.py          # Configuration and settings
├── models/
│   └── schemas.py           # Pydantic request/response models
├── services/
│   ├── auth.py              # Authentication service
│   └── test_executor.py     # Test execution services
├── utils/
│   └── helpers.py           # Utility functions
└── scripts/
    └── ...                  # Utility scripts
```

## Installation

```bash
# Install dependencies
pip install -r backend/requirements.txt
```

## Running

```bash
# From project root
python backend/api/main.py

# Or using uvicorn directly
cd backend
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Environment Variables

Set `OPENAI_API_KEY` in your environment or `.env` file:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## API Documentation

Once running, visit:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

