"""
Unit tests for base connector interface.

Tests the abstract base class and data structures.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from src.base import BaseConnector, ConnectionResult, ModelResponse, ConnectionStatus


class TestConnectionResult:
    """Test ConnectionResult dataclass."""
    
    def test_connection_result_creation(self):
        """Test ConnectionResult creation with all fields."""
        result = ConnectionResult(
            status=ConnectionStatus.SUCCESS,
            message="Test successful",
            latency_ms=123.45,
            model_info={"model": "test-model"}
        )
        
        assert result.status == ConnectionStatus.SUCCESS
        assert result.message == "Test successful"
        assert result.latency_ms == 123.45
        assert result.model_info == {"model": "test-model"}
    
    def test_connection_result_minimal(self):
        """Test ConnectionResult creation with minimal fields."""
        result = ConnectionResult(
            status=ConnectionStatus.FAILED,
            message="Test failed"
        )
        
        assert result.status == ConnectionStatus.FAILED
        assert result.message == "Test failed"
        assert result.latency_ms is None
        assert result.model_info is None


class TestModelResponse:
    """Test ModelResponse dataclass."""
    
    def test_model_response_creation(self):
        """Test ModelResponse creation with all fields."""
        response = ModelResponse(
            content="Test response",
            model="gpt-3.5-turbo",
            usage={"prompt_tokens": 10, "completion_tokens": 20},
            latency_ms=150.0,
            metadata={"finish_reason": "stop"}
        )
        
        assert response.content == "Test response"
        assert response.model == "gpt-3.5-turbo"
        assert response.usage == {"prompt_tokens": 10, "completion_tokens": 20}
        assert response.latency_ms == 150.0
        assert response.metadata == {"finish_reason": "stop"}


class TestConnectionStatus:
    """Test ConnectionStatus enum."""
    
    def test_connection_status_values(self):
        """Test ConnectionStatus enum values."""
        assert ConnectionStatus.SUCCESS.value == "success"
        assert ConnectionStatus.FAILED.value == "failed"
        assert ConnectionStatus.INVALID_CREDENTIALS.value == "invalid_credentials"
        assert ConnectionStatus.RATE_LIMITED.value == "rate_limited"
        assert ConnectionStatus.TIMEOUT.value == "timeout"


class TestBaseConnector:
    """Test BaseConnector abstract class."""
    
    def test_base_connector_initialization(self):
        """Test BaseConnector initialization."""
        # Create a concrete implementation for testing
        class TestConnector(BaseConnector):
            async def test_connection(self):
                return ConnectionResult(ConnectionStatus.SUCCESS, "Test")
            
            async def send_prompt(self, prompt, system_message=None, **kwargs):
                return ModelResponse("Test", "test-model", {}, 100.0, {})
            
            def get_model_info(self):
                return {"model": "test"}
            
            @property
            def provider_name(self):
                return "test"
        
        connector = TestConnector("test-key", "test-model", extra_param="value")
        
        assert connector.api_key == "test-key"
        assert connector.model == "test-model"
        assert connector.config == {"extra_param": "value"}
    
    def test_base_connector_abstract_methods(self):
        """Test that BaseConnector cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseConnector("test-key", "test-model")
    
    def test_base_connector_must_implement_methods(self):
        """Test that concrete classes must implement all abstract methods."""
        class IncompleteConnector(BaseConnector):
            pass
        
        with pytest.raises(TypeError):
            IncompleteConnector("test-key", "test-model")

