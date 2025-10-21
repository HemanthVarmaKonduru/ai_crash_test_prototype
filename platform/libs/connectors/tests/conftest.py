"""
Pytest configuration and fixtures for connectors tests.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient for testing."""
    with pytest.Mock() as mock_client:
        mock_client.return_value.__aenter__ = AsyncMock()
        mock_client.return_value.__aexit__ = AsyncMock()
        yield mock_client


@pytest.fixture
def openai_connector():
    """Create OpenAI connector for testing."""
    from src.openai_connector import OpenAIConnector
    return OpenAIConnector(
        api_key="sk-test123",
        model="gpt-3.5-turbo"
    )


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "choices": [{"message": {"content": "Test response"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        "id": "chatcmpl-123"
    }
    return response


@pytest.fixture
def mock_connection_response():
    """Mock connection test response."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "choices": [{"message": {"content": "Connection successful."}}]
    }
    return response


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

