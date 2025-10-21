"""
Unit tests for WebSocket event publishing.

Tests event creation, publishing, subscription, and history tracking.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.events import (
    EventPublisher, WebSocketEvent, EventType,
    publish_model_connected, publish_model_status_update
)


class TestWebSocketEvent:
    """Test WebSocketEvent dataclass."""
    
    def test_websocket_event_creation(self):
        """Test WebSocketEvent creation with all fields."""
        event = WebSocketEvent(
            event_type=EventType.MODEL_CONNECTED,
            user_id="user123",
            data={"model_id": "model123", "status": "connected"},
            timestamp="2025-01-01T00:00:00Z",
            event_id="event-123"
        )
        
        assert event.event_type == EventType.MODEL_CONNECTED
        assert event.user_id == "user123"
        assert event.data == {"model_id": "model123", "status": "connected"}
        assert event.timestamp == "2025-01-01T00:00:00Z"
        assert event.event_id == "event-123"
    
    def test_websocket_event_minimal(self):
        """Test WebSocketEvent creation with minimal fields."""
        event = WebSocketEvent(
            event_type=EventType.MODEL_DISCONNECTED,
            user_id="user123",
            data={"model_id": "model123"},
            timestamp="2025-01-01T00:00:00Z"
        )
        
        assert event.event_type == EventType.MODEL_DISCONNECTED
        assert event.user_id == "user123"
        assert event.data == {"model_id": "model123"}
        assert event.event_id is None


class TestEventType:
    """Test EventType enum."""
    
    def test_event_type_values(self):
        """Test EventType enum values."""
        assert EventType.MODEL_CONNECTED.value == "model_connected"
        assert EventType.MODEL_DISCONNECTED.value == "model_disconnected"
        assert EventType.MODEL_STATUS_UPDATE.value == "model_status_update"
        assert EventType.TEST_STARTED.value == "test_started"
        assert EventType.TEST_COMPLETED.value == "test_completed"
        assert EventType.ERROR_OCCURRED.value == "error_occurred"


class TestEventPublisher:
    """Test EventPublisher functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.publisher = EventPublisher()
    
    def test_initialization(self):
        """Test EventPublisher initialization."""
        assert isinstance(self.publisher._subscribers, dict)
        assert isinstance(self.publisher._event_history, list)
        assert len(self.publisher._subscribers) == 0
        assert len(self.publisher._event_history) == 0
    
    @pytest.mark.asyncio
    async def test_publish_event_success(self):
        """Test successful event publishing."""
        with patch.object(self.publisher, '_notify_subscribers', new_callable=AsyncMock) as mock_notify:
            result = await self.publisher.publish_event(
                event_type=EventType.MODEL_CONNECTED,
                user_id="user123",
                data={"model_id": "model123"},
                event_id="event-123"
            )
            
            assert result is True
            mock_notify.assert_called_once()
            
            # Verify event is stored in history
            assert len(self.publisher._event_history) == 1
            event = self.publisher._event_history[0]
            assert event.event_type == EventType.MODEL_CONNECTED
            assert event.user_id == "user123"
            assert event.data == {"model_id": "model123"}
            assert event.event_id == "event-123"
    
    @pytest.mark.asyncio
    async def test_publish_event_with_timestamp(self):
        """Test event publishing with automatic timestamp."""
        with patch('src.events.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value.isoformat.return_value = "2025-01-01T00:00:00Z"
            
            with patch.object(self.publisher, '_notify_subscribers', new_callable=AsyncMock):
                await self.publisher.publish_event(
                    event_type=EventType.MODEL_CONNECTED,
                    user_id="user123",
                    data={"model_id": "model123"}
                )
                
                event = self.publisher._event_history[0]
                assert event.timestamp == "2025-01-01T00:00:00Z"
    
    @pytest.mark.asyncio
    async def test_publish_event_error_handling(self):
        """Test event publishing error handling."""
        with patch.object(self.publisher, '_notify_subscribers', new_callable=AsyncMock) as mock_notify:
            mock_notify.side_effect = Exception("Notification error")
            
            with patch('builtins.print') as mock_print:
                result = await self.publisher.publish_event(
                    event_type=EventType.MODEL_CONNECTED,
                    user_id="user123",
                    data={"model_id": "model123"}
                )
                
                assert result is False
                mock_print.assert_called_with("Failed to publish event: Notification error")
    
    @pytest.mark.asyncio
    async def test_notify_subscribers(self):
        """Test subscriber notification."""
        # Add a mock subscriber
        mock_callback = AsyncMock()
        self.publisher._subscribers["user123"] = [mock_callback]
        
        event = WebSocketEvent(
            event_type=EventType.MODEL_CONNECTED,
            user_id="user123",
            data={"model_id": "model123"},
            timestamp="2025-01-01T00:00:00Z"
        )
        
        with patch('builtins.print') as mock_print:
            await self.publisher._notify_subscribers(event)
            
            # Verify callback was called
            mock_callback.assert_called_once_with(event)
            
            # Verify logging
            mock_print.assert_called()
    
    @pytest.mark.asyncio
    async def test_subscribe(self):
        """Test event subscription."""
        mock_callback = AsyncMock()
        
        await self.publisher.subscribe("user123", mock_callback)
        
        assert "user123" in self.publisher._subscribers
        assert mock_callback in self.publisher._subscribers["user123"]
    
    @pytest.mark.asyncio
    async def test_subscribe_multiple_callbacks(self):
        """Test multiple callbacks for same user."""
        mock_callback1 = AsyncMock()
        mock_callback2 = AsyncMock()
        
        await self.publisher.subscribe("user123", mock_callback1)
        await self.publisher.subscribe("user123", mock_callback2)
        
        assert len(self.publisher._subscribers["user123"]) == 2
        assert mock_callback1 in self.publisher._subscribers["user123"]
        assert mock_callback2 in self.publisher._subscribers["user123"]
    
    @pytest.mark.asyncio
    async def test_unsubscribe(self):
        """Test event unsubscription."""
        mock_callback = AsyncMock()
        
        # Subscribe first
        await self.publisher.subscribe("user123", mock_callback)
        assert mock_callback in self.publisher._subscribers["user123"]
        
        # Then unsubscribe
        await self.publisher.unsubscribe("user123", mock_callback)
        assert mock_callback not in self.publisher._subscribers["user123"]
    
    @pytest.mark.asyncio
    async def test_get_event_history(self):
        """Test event history retrieval."""
        # Add some events to history
        event1 = WebSocketEvent(
            event_type=EventType.MODEL_CONNECTED,
            user_id="user123",
            data={"model_id": "model1"},
            timestamp="2025-01-01T00:00:00Z"
        )
        
        event2 = WebSocketEvent(
            event_type=EventType.MODEL_STATUS_UPDATE,
            user_id="user123",
            data={"model_id": "model1", "status": "active"},
            timestamp="2025-01-01T00:01:00Z"
        )
        
        event3 = WebSocketEvent(
            event_type=EventType.MODEL_CONNECTED,
            user_id="user456",
            data={"model_id": "model2"},
            timestamp="2025-01-01T00:02:00Z"
        )
        
        self.publisher._event_history = [event1, event2, event3]
        
        # Get history for user123
        history = await self.publisher.get_event_history("user123")
        assert len(history) == 2
        assert history[0] == event1
        assert history[1] == event2
        
        # Get history with event type filter
        history_filtered = await self.publisher.get_event_history(
            "user123", 
            EventType.MODEL_CONNECTED
        )
        assert len(history_filtered) == 1
        assert history_filtered[0] == event1
        
        # Get history with limit
        history_limited = await self.publisher.get_event_history("user123", limit=1)
        assert len(history_limited) == 1
        assert history_limited[0] == event2  # Most recent event


class TestEventHelpers:
    """Test event helper functions."""
    
    @pytest.mark.asyncio
    async def test_publish_model_connected(self):
        """Test publish_model_connected helper function."""
        with patch('src.events.event_publisher') as mock_publisher:
            mock_publisher.publish_event = AsyncMock(return_value=True)
            
            result = await publish_model_connected(
                user_id="user123",
                model_id="model123",
                model_info={"model": "gpt-3.5-turbo"}
            )
            
            assert result is True
            mock_publisher.publish_event.assert_called_once_with(
                event_type=EventType.MODEL_CONNECTED,
                user_id="user123",
                data={
                    "model_id": "model123",
                    "model_info": {"model": "gpt-3.5-turbo"},
                    "status": "connected"
                }
            )
    
    @pytest.mark.asyncio
    async def test_publish_model_status_update(self):
        """Test publish_model_status_update helper function."""
        with patch('src.events.event_publisher') as mock_publisher:
            mock_publisher.publish_event = AsyncMock(return_value=True)
            
            result = await publish_model_status_update(
                user_id="user123",
                model_id="model123",
                status="active",
                details={"latency_ms": 245.5}
            )
            
            assert result is True
            mock_publisher.publish_event.assert_called_once_with(
                event_type=EventType.MODEL_STATUS_UPDATE,
                user_id="user123",
                data={
                    "model_id": "model123",
                    "status": "active",
                    "details": {"latency_ms": 245.5}
                }
            )
