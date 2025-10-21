"""
Unit tests for API Gateway main application.

Tests FastAPI endpoints, authentication, and request/response handling.
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import status
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from main import app, get_current_user


class TestAPIGateway:
    """Test API Gateway functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.client = TestClient(app)
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "api-gateway"
    
    def test_get_current_user(self):
        """Test get_current_user dependency."""
        user_id = get_current_user()
        assert user_id == "demo-user-123"
    
    @patch('main.OpenAIConnector')
    @patch('main.credential_storage')
    @patch('main.metadata_storage')
    async def test_connect_model_success(self, mock_metadata_storage, mock_credential_storage, mock_connector_class):
        """Test successful model connection."""
        # Mock connector test_connection
        mock_connector = Mock()
        mock_connector.test_connection = AsyncMock(return_value=Mock(
            status=Mock(value="success"),
            message="Connection successful",
            latency_ms=245.5,
            model_info={"model": "gpt-3.5-turbo", "provider": "openai"}
        ))
        mock_connector_class.return_value = mock_connector
        
        # Mock storage operations
        mock_credential_storage.store_credentials = AsyncMock(return_value=Mock(
            status=Mock(value="success"),
            message="Credentials stored successfully"
        ))
        mock_metadata_storage.store_metadata = AsyncMock(return_value=Mock(
            status=Mock(value="success"),
            message="Metadata stored successfully"
        ))
        
        # Test request
        request_data = {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "api_key": "sk-test123",
            "name": "Test Model",
            "config": {"temperature": 0.7}
        }
        
        response = self.client.post("/models/connect", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "Model connected successfully" in data["message"]
        assert data["model_id"] == "demo-user-123:openai:gpt-3.5-turbo"
        assert data["latency_ms"] == 245.5
        assert data["model_info"]["model"] == "gpt-3.5-turbo"
    
    @patch('main.OpenAIConnector')
    async def test_connect_model_unsupported_provider(self, mock_connector_class):
        """Test model connection with unsupported provider."""
        request_data = {
            "provider": "anthropic",
            "model": "claude-3",
            "api_key": "ant-test123"
        }
        
        response = self.client.post("/models/connect", json=request_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Only OpenAI provider is currently supported" in data["detail"]
    
    @patch('main.OpenAIConnector')
    async def test_connect_model_connection_failed(self, mock_connector_class):
        """Test model connection when connection test fails."""
        # Mock failed connection test
        mock_connector = Mock()
        mock_connector.test_connection = AsyncMock(return_value=Mock(
            status=Mock(value="failed"),
            message="Invalid API key"
        ))
        mock_connector_class.return_value = mock_connector
        
        request_data = {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "api_key": "sk-invalid"
        }
        
        response = self.client.post("/models/connect", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is False
        assert "Connection failed" in data["message"]
    
    @patch('main.OpenAIConnector')
    @patch('main.credential_storage')
    async def test_connect_model_credential_storage_failed(self, mock_credential_storage, mock_connector_class):
        """Test model connection when credential storage fails."""
        # Mock successful connection test
        mock_connector = Mock()
        mock_connector.test_connection = AsyncMock(return_value=Mock(
            status=Mock(value="success"),
            message="Connection successful"
        ))
        mock_connector_class.return_value = mock_connector
        
        # Mock failed credential storage
        mock_credential_storage.store_credentials = AsyncMock(return_value=Mock(
            status=Mock(value="failed"),
            message="Storage error"
        ))
        
        request_data = {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "api_key": "sk-test123"
        }
        
        response = self.client.post("/models/connect", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is False
        assert "Failed to store credentials" in data["message"]
    
    @patch('main.OpenAIConnector')
    @patch('main.credential_storage')
    @patch('main.metadata_storage')
    async def test_connect_model_metadata_storage_failed(self, mock_metadata_storage, mock_credential_storage, mock_connector_class):
        """Test model connection when metadata storage fails."""
        # Mock successful connection test
        mock_connector = Mock()
        mock_connector.test_connection = AsyncMock(return_value=Mock(
            status=Mock(value="success"),
            message="Connection successful"
        ))
        mock_connector_class.return_value = mock_connector
        
        # Mock successful credential storage
        mock_credential_storage.store_credentials = AsyncMock(return_value=Mock(
            status=Mock(value="success"),
            message="Credentials stored successfully"
        ))
        
        # Mock failed metadata storage
        mock_metadata_storage.store_metadata = AsyncMock(return_value=Mock(
            status=Mock(value="failed"),
            message="Metadata storage error"
        ))
        
        request_data = {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "api_key": "sk-test123"
        }
        
        response = self.client.post("/models/connect", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is False
        assert "Failed to store metadata" in data["message"]
    
    @patch('main.metadata_storage')
    async def test_list_models_success(self, mock_metadata_storage):
        """Test successful model listing."""
        # Mock successful model listing
        mock_metadata_storage.list_user_models = AsyncMock(return_value=Mock(
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
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["models"]) == 2
        assert data["models"][0]["model"] == "gpt-3.5-turbo"
        assert data["models"][1]["model"] == "gpt-4"
    
    @patch('main.metadata_storage')
    async def test_list_models_failed(self, mock_metadata_storage):
        """Test model listing when storage fails."""
        # Mock failed model listing
        mock_metadata_storage.list_user_models = AsyncMock(return_value=Mock(
            status=Mock(value="failed"),
            message="Storage error"
        ))
        
        response = self.client.get("/models")
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Failed to list models" in data["detail"]
    
    def test_connect_model_invalid_json(self):
        """Test model connection with invalid JSON."""
        response = self.client.post("/models/connect", data="invalid json")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_connect_model_missing_required_fields(self):
        """Test model connection with missing required fields."""
        request_data = {
            "provider": "openai"
            # Missing model and api_key
        }
        
        response = self.client.post("/models/connect", json=request_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @patch('main.OpenAIConnector')
    async def test_connect_model_internal_error(self, mock_connector_class):
        """Test model connection with internal server error."""
        # Mock connector to raise exception
        mock_connector_class.side_effect = Exception("Internal error")
        
        request_data = {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "api_key": "sk-test123"
        }
        
        response = self.client.post("/models/connect", json=request_data)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Internal server error" in data["detail"]
    
    @patch('main.metadata_storage')
    async def test_list_models_internal_error(self, mock_metadata_storage):
        """Test model listing with internal server error."""
        # Mock storage to raise exception
        mock_metadata_storage.list_user_models = AsyncMock(side_effect=Exception("Internal error"))
        
        response = self.client.get("/models")
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Internal server error" in data["detail"]

