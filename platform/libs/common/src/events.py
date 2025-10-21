"""
WebSocket event publishing utilities.

Handles real-time event publishing for model connections and status updates.
"""

import json
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class EventType(Enum):
    """WebSocket event types."""
    MODEL_CONNECTED = "model_connected"
    MODEL_DISCONNECTED = "model_disconnected"
    MODEL_STATUS_UPDATE = "model_status_update"
    TEST_STARTED = "test_started"
    TEST_COMPLETED = "test_completed"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class WebSocketEvent:
    """WebSocket event data structure."""
    event_type: EventType
    user_id: str
    data: Dict[str, Any]
    timestamp: str
    event_id: Optional[str] = None


class EventPublisher:
    """
    WebSocket event publisher for real-time updates.
    
    Handles publishing events to connected clients via WebSocket connections.
    """
    
    def __init__(self):
        """Initialize event publisher."""
        # In production, this would connect to Redis or message queue
        self._subscribers: Dict[str, List[callable]] = {}
        self._event_history: List[WebSocketEvent] = []
    
    async def publish_event(
        self, 
        event_type: EventType, 
        user_id: str, 
        data: Dict[str, Any],
        event_id: Optional[str] = None
    ) -> bool:
        """
        Publish a WebSocket event.
        
        Args:
            event_type: Type of event to publish
            user_id: Target user ID
            data: Event data payload
            event_id: Optional event identifier
            
        Returns:
            True if event was published successfully
        """
        try:
            # Create event
            event = WebSocketEvent(
                event_type=event_type,
                user_id=user_id,
                data=data,
                timestamp=datetime.utcnow().isoformat(),
                event_id=event_id
            )
            
            # Store in history (for debugging/replay)
            self._event_history.append(event)
            
            # Notify subscribers
            await self._notify_subscribers(event)
            
            return True
            
        except Exception as e:
            print(f"Failed to publish event: {e}")
            return False
    
    async def _notify_subscribers(self, event: WebSocketEvent):
        """
        Notify all subscribers of an event.
        
        Args:
            event: WebSocket event to notify about
        """
        # In production, this would send to actual WebSocket connections
        # For now, just log the event
        print(f"WebSocket Event: {event.event_type.value} for user {event.user_id}")
        print(f"Data: {json.dumps(event.data, indent=2)}")
    
    async def subscribe(self, user_id: str, callback: callable):
        """
        Subscribe to events for a specific user.
        
        Args:
            user_id: User to subscribe for
            callback: Callback function to handle events
        """
        if user_id not in self._subscribers:
            self._subscribers[user_id] = []
        self._subscribers[user_id].append(callback)
    
    async def unsubscribe(self, user_id: str, callback: callable):
        """
        Unsubscribe from events for a specific user.
        
        Args:
            user_id: User to unsubscribe from
            callback: Callback function to remove
        """
        if user_id in self._subscribers:
            if callback in self._subscribers[user_id]:
                self._subscribers[user_id].remove(callback)
    
    async def get_event_history(
        self, 
        user_id: str, 
        event_type: Optional[EventType] = None,
        limit: int = 100
    ) -> List[WebSocketEvent]:
        """
        Get event history for a user.
        
        Args:
            user_id: User to get history for
            event_type: Optional event type filter
            limit: Maximum number of events to return
            
        Returns:
            List of WebSocket events
        """
        # Filter events for user
        user_events = [
            event for event in self._event_history 
            if event.user_id == user_id
        ]
        
        # Filter by event type if specified
        if event_type:
            user_events = [
                event for event in user_events 
                if event.event_type == event_type
            ]
        
        # Return most recent events
        return user_events[-limit:]


# Global event publisher instance
event_publisher = EventPublisher()


async def publish_model_connected(
    user_id: str, 
    model_id: str, 
    model_info: Dict[str, Any]
) -> bool:
    """
    Publish model connected event.
    
    Args:
        user_id: User who connected the model
        model_id: Connected model identifier
        model_info: Model information
        
    Returns:
        True if event was published successfully
    """
    return await event_publisher.publish_event(
        event_type=EventType.MODEL_CONNECTED,
        user_id=user_id,
        data={
            "model_id": model_id,
            "model_info": model_info,
            "status": "connected"
        }
    )


async def publish_model_status_update(
    user_id: str, 
    model_id: str, 
    status: str, 
    details: Dict[str, Any]
) -> bool:
    """
    Publish model status update event.
    
    Args:
        user_id: User who owns the model
        model_id: Model identifier
        status: New status
        details: Status details
        
    Returns:
        True if event was published successfully
    """
    return await event_publisher.publish_event(
        event_type=EventType.MODEL_STATUS_UPDATE,
        user_id=user_id,
        data={
            "model_id": model_id,
            "status": status,
            "details": details
        }
    )

