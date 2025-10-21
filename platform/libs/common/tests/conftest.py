"""
Pytest configuration and fixtures for common library tests.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from src.events import EventPublisher, WebSocketEvent, EventType


@pytest.fixture
def event_publisher():
    """Create EventPublisher instance for testing."""
    return EventPublisher()


@pytest.fixture
def sample_websocket_event():
    """Sample WebSocket event for testing."""
    return WebSocketEvent(
        event_type=EventType.MODEL_CONNECTED,
        user_id="user123",
        data={"model_id": "model123", "status": "connected"},
        timestamp="2025-01-01T00:00:00Z",
        event_id="event-123"
    )


@pytest.fixture
def mock_callback():
    """Mock callback function for testing."""
    return AsyncMock()


@pytest.fixture
def sample_model_info():
    """Sample model information for testing."""
    return {
        "model": "gpt-3.5-turbo",
        "provider": "openai",
        "status": "connected",
        "latency_ms": 245.5
    }

