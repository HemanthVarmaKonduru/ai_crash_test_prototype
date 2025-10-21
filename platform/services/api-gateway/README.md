# API Gateway Service

Single entrypoint for the Adversarial Sandbox platform.

## Overview

The API Gateway handles:
- Authentication and authorization
- Request validation and routing
- Rate limiting and security
- Model connection management

## Endpoints

### Model Connection

#### `POST /models/connect`

Connect a new model to the platform.

**Request Body:**
```json
{
  "provider": "openai",
  "model": "gpt-3.5-turbo", 
  "api_key": "sk-...",
  "name": "My GPT-3.5 Model",
  "config": {
    "temperature": 0.7,
    "max_tokens": 1000
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Model connected successfully",
  "model_id": "demo-user-123:openai:gpt-3.5-turbo",
  "latency_ms": 245.5,
  "model_info": {
    "model": "gpt-3.5-turbo",
    "provider": "openai",
    "response": "Connection successful."
  }
}
```

#### `GET /models`

List all models for the current user.

**Response:**
```json
{
  "models": [
    {
      "model_id": "demo-user-123:openai:gpt-3.5-turbo",
      "user_id": "demo-user-123",
      "provider": "openai",
      "model": "gpt-3.5-turbo",
      "name": "My GPT-3.5 Model",
      "status": "connected",
      "latency_ms": 245.5,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### Health Check

#### `GET /health`

Service health check.

**Response:**
```json
{
  "status": "healthy",
  "service": "api-gateway"
}
```

## Development

### Installation

```bash
cd platform/services/api-gateway
pip install -e .
```

### Running

```bash
python src/main.py
```

The service will start on `http://localhost:8000`

### API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Architecture

### Authentication

Currently uses simplified authentication (hardcoded user ID). In production:

1. **JWT Token Validation** - Validate incoming JWT tokens
2. **User Extraction** - Extract user ID from token claims
3. **Permission Checking** - Verify user permissions for operations

### Security

- **CORS Configuration** - Configured for frontend access
- **Input Validation** - Pydantic models for request validation
- **Error Handling** - Proper HTTP status codes and error messages

### Dependencies

- **FastAPI** - Web framework
- **Pydantic** - Data validation
- **Connectors Library** - Model provider integration
- **Storage Library** - Secure credential storage

