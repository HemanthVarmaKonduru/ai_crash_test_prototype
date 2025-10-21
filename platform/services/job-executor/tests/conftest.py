"""
Pytest configuration and fixtures for job executor tests.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from main import app

@pytest.fixture
def api_client():
    """Create test client for Job Executor API."""
    return TestClient(app)

@pytest.fixture
def sample_job_request():
    """Sample job request for testing."""
    return {
        "test_suite": "safety",
        "model_id": "demo-user-123:openai:gpt-3.5-turbo",
        "user_id": "demo-user-123",
        "config": {
            "temperature": 0.7,
            "max_tokens": 1000
        }
    }

@pytest.fixture
def mock_websocket():
    """Mock WebSocket for testing."""
    mock_ws = Mock()
    mock_ws.accept = AsyncMock()
    mock_ws.receive_text = AsyncMock()
    mock_ws.close = AsyncMock()
    return mock_ws

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

