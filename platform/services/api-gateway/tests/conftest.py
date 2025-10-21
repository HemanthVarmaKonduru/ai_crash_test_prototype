"""
Pytest configuration and fixtures for API Gateway tests.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from main import app


@pytest.fixture
def client():
    """Create test client for API Gateway."""
    return TestClient(app)


@pytest.fixture
def sample_connection_request():
    """Sample model connection request."""
    return {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "api_key": "sk-test123456789",
        "name": "Test GPT-3.5 Model",
        "config": {
            "temperature": 0.7,
            "max_tokens": 1000
        }
    }


@pytest.fixture
def sample_connection_response():
    """Sample model connection response."""
    return {
        "success": True,
        "message": "Model connected successfully",
        "model_id": "demo-user-123:openai:gpt-3.5-turbo",
        "latency_ms": 245.5,
        "model_info": {
            "model": "gpt-3.5-turbo",
            "provider": "openai",
            "response": "Connection successful."
        }
    }


@pytest.fixture
def sample_models_list():
    """Sample models list response."""
    return {
        "models": [
            {
                "model_id": "demo-user-123:openai:gpt-3.5-turbo",
                "user_id": "demo-user-123",
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "name": "GPT-3.5 Model",
                "status": "connected",
                "latency_ms": 245.5,
                "created_at": "2025-01-01T00:00:00Z"
            }
        ]
    }

