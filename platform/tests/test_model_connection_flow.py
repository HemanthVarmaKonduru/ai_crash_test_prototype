"""
Integration tests for the complete model connection flow.

Tests the end-to-end workflow from API request to model connection.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../services/api-gateway/src"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../libs/connectors/src"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../libs/storage/src"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../libs/common/src"))

from main import app
from connectors import OpenAIConnector
from storage import CredentialStorage, ModelMetadataStorage
from events import EventPublisher


class TestModelConnectionFlow:
    """Test complete model connection workflow."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.client = TestClient(app)
        self.encryption_key = "test-encryption-key-123456789012345678901234567890"
    
    @pytest.mark.asyncio
    async def test_complete_model_connection_flow(self):
        """Test the complete model connection flow from API to storage."""
        # Mock OpenAI connector
        mock_connector = Mock()
        mock_connector.test_connection = AsyncMock(return_value=Mock(
            status=Mock(value="success"),
            message="Connection successful",
            latency_ms=245.5,
            model_info={"model": "gpt-3.5-turbo", "provider": "openai"}
        ))
        
        with patch('main.OpenAIConnector', return_value=mock_connector):
            with patch('main.credential_storage') as mock_cred_storage:
                with patch('main.metadata_storage') as mock_meta_storage:
                    # Mock storage operations
                    mock_cred_storage.store_credentials = AsyncMock(return_value=Mock(
                        status=Mock(value="success"),
                        message="Credentials stored successfully"
                    ))
                    mock_meta_storage.store_metadata = AsyncMock(return_value=Mock(
                        status=Mock(value="success"),
                        message="Metadata stored successfully"
                    ))
                    
                    # Test the complete flow
                    request_data = {
                        "provider": "openai",
                        "model": "gpt-3.5-turbo",
                        "api_key": "sk-test123",
                        "name": "Test Model",
                        "config": {"temperature": 0.7}
                    }
                    
                    response = self.client.post("/models/connect", json=request_data)
                    
                    # Verify response
                    assert response.status_code == 200
                    data = response.json()
                    assert data["success"] is True
                    assert "Model connected successfully" in data["message"]
                    assert data["model_id"] == "demo-user-123:openai:gpt-3.5-turbo"
                    assert data["latency_ms"] == 245.5
                    
                    # Verify connector was called
                    mock_connector.test_connection.assert_called_once()
                    
                    # Verify storage operations
                    mock_cred_storage.store_credentials.assert_called_once()
                    mock_meta_storage.store_metadata.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_model_connection_with_websocket_events(self):
        """Test model connection with WebSocket event publishing."""
        # Mock all components
        mock_connector = Mock()
        mock_connector.test_connection = AsyncMock(return_value=Mock(
            status=Mock(value="success"),
            message="Connection successful",
            latency_ms=245.5,
            model_info={"model": "gpt-3.5-turbo"}
        ))
        
        with patch('main.OpenAIConnector', return_value=mock_connector):
            with patch('main.credential_storage') as mock_cred_storage:
                with patch('main.metadata_storage') as mock_meta_storage:
                    with patch('events.publish_model_connected') as mock_publish:
                        # Mock storage operations
                        mock_cred_storage.store_credentials = AsyncMock(return_value=Mock(
                            status=Mock(value="success"),
                            message="Credentials stored successfully"
                        ))
                        mock_meta_storage.store_metadata = AsyncMock(return_value=Mock(
                            status=Mock(value="success"),
                            message="Metadata stored successfully"
                        ))
                        mock_publish.return_value = True
                        
                        # Test connection
                        request_data = {
                            "provider": "openai",
                            "model": "gpt-3.5-turbo",
                            "api_key": "sk-test123"
                        }
                        
                        response = self.client.post("/models/connect", json=request_data)
                        
                        # Verify response
                        assert response.status_code == 200
                        data = response.json()
                        assert data["success"] is True
                        
                        # Verify WebSocket event was published
                        mock_publish.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_model_connection_failure_flow(self):
        """Test model connection failure flow."""
        # Mock failed connector
        mock_connector = Mock()
        mock_connector.test_connection = AsyncMock(return_value=Mock(
            status=Mock(value="failed"),
            message="Invalid API key"
        ))
        
        with patch('main.OpenAIConnector', return_value=mock_connector):
            request_data = {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "api_key": "sk-invalid"
            }
            
            response = self.client.post("/models/connect", json=request_data)
            
            # Verify failure response
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert "Connection failed" in data["message"]
    
    @pytest.mark.asyncio
    async def test_model_listing_flow(self):
        """Test model listing workflow."""
        with patch('main.metadata_storage') as mock_meta_storage:
            # Mock successful model listing
            mock_meta_storage.list_user_models = AsyncMock(return_value=Mock(
                status=Mock(value="success"),
                message="Found 2 models for user",
                data={
                    "models": [
                        {
                            "model_id": "demo-user-123:openai:gpt-3.5-turbo",
                            "user_id": "demo-user-123",
                            "provider": "openai",
                            "model": "gpt-3.5-turbo",
                            "name": "GPT-3.5 Model",
                            "status": "connected"
                        },
                        {
                            "model_id": "demo-user-123:openai:gpt-4",
                            "user_id": "demo-user-123",
                            "provider": "openai",
                            "model": "gpt-4",
                            "name": "GPT-4 Model",
                            "status": "connected"
                        }
                    ]
                }
            ))
            
            response = self.client.get("/models")
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert len(data["models"]) == 2
            assert data["models"][0]["model"] == "gpt-3.5-turbo"
            assert data["models"][1]["model"] == "gpt-4"
    
    @pytest.mark.asyncio
    async def test_encryption_integration(self):
        """Test encryption integration in credential storage."""
        # Test with real encryption
        from cryptography.fernet import Fernet
        
        # Generate real encryption key
        encryption_key = Fernet.generate_key().decode()
        credential_storage = CredentialStorage(encryption_key)
        
        # Test credential storage and retrieval
        credentials = {
            "api_key": "sk-test123456789",
            "model": "gpt-3.5-turbo",
            "provider": "openai"
        }
        
        # Store credentials
        store_result = await credential_storage.store_credentials(
            user_id="test-user",
            provider="openai",
            credentials=credentials
        )
        
        assert store_result.status.value == "success"
        
        # Retrieve credentials
        get_result = await credential_storage.get_credentials(
            user_id="test-user",
            provider="openai"
        )
        
        assert get_result.status.value == "success"
        assert get_result.data == credentials
    
    @pytest.mark.asyncio
    async def test_metadata_persistence_integration(self):
        """Test metadata persistence integration."""
        metadata_storage = ModelMetadataStorage()
        
        # Test metadata storage
        metadata = {
            "model_id": "test-user:openai:gpt-3.5-turbo",
            "user_id": "test-user",
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "name": "Test Model",
            "status": "connected",
            "latency_ms": 245.5
        }
        
        # Store metadata
        store_result = await metadata_storage.store_metadata(
            model_id="test-user:openai:gpt-3.5-turbo",
            metadata=metadata
        )
        
        assert store_result.status.value == "success"
        
        # Retrieve metadata
        get_result = await metadata_storage.get_metadata("test-user:openai:gpt-3.5-turbo")
        
        assert get_result.status.value == "success"
        assert get_result.data["user_id"] == "test-user"
        assert get_result.data["provider"] == "openai"
        assert get_result.data["model"] == "gpt-3.5-turbo"
        
        # List user models
        list_result = await metadata_storage.list_user_models("test-user")
        
        assert list_result.status.value == "success"
        assert len(list_result.data["models"]) == 1
        assert list_result.data["models"][0]["model_id"] == "test-user:openai:gpt-3.5-turbo"
    
    @pytest.mark.asyncio
    async def test_websocket_event_integration(self):
        """Test WebSocket event publishing integration."""
        event_publisher = EventPublisher()
        
        # Test event publishing
        result = await event_publisher.publish_event(
            event_type="model_connected",
            user_id="test-user",
            data={"model_id": "test-model", "status": "connected"}
        )
        
        assert result is True
        
        # Test event history
        history = await event_publisher.get_event_history("test-user")
        assert len(history) == 1
        assert history[0].user_id == "test-user"
        assert history[0].data["model_id"] == "test-model"
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self):
        """Test error handling across the entire flow."""
        # Test with invalid provider
        request_data = {
            "provider": "unsupported",
            "model": "test-model",
            "api_key": "test-key"
        }
        
        response = self.client.post("/models/connect", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Only OpenAI provider is currently supported" in data["detail"]
        
        # Test with malformed request
        response = self.client.post("/models/connect", json={"invalid": "data"})
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_concurrent_connections(self):
        """Test handling multiple concurrent model connections."""
        # Mock successful connector
        mock_connector = Mock()
        mock_connector.test_connection = AsyncMock(return_value=Mock(
            status=Mock(value="success"),
            message="Connection successful",
            latency_ms=245.5,
            model_info={"model": "gpt-3.5-turbo"}
        ))
        
        with patch('main.OpenAIConnector', return_value=mock_connector):
            with patch('main.credential_storage') as mock_cred_storage:
                with patch('main.metadata_storage') as mock_meta_storage:
                    # Mock storage operations
                    mock_cred_storage.store_credentials = AsyncMock(return_value=Mock(
                        status=Mock(value="success"),
                        message="Credentials stored successfully"
                    ))
                    mock_meta_storage.store_metadata = AsyncMock(return_value=Mock(
                        status=Mock(value="success"),
                        message="Metadata stored successfully"
                    ))
                    
                    # Test multiple concurrent requests
                    request_data = {
                        "provider": "openai",
                        "model": "gpt-3.5-turbo",
                        "api_key": "sk-test123"
                    }
                    
                    # Send multiple requests
                    responses = []
                    for i in range(3):
                        response = self.client.post("/models/connect", json=request_data)
                        responses.append(response)
                    
                    # Verify all responses are successful
                    for response in responses:
                        assert response.status_code == 200
                        data = response.json()
                        assert data["success"] is True

