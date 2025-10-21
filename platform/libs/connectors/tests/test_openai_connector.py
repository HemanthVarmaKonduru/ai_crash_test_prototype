"""
Unit tests for OpenAI connector.

Tests OpenAI API integration, connection testing, and prompt sending.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import httpx
from src.openai_connector import OpenAIConnector
from src.base import ConnectionStatus, ModelResponse


class TestOpenAIConnector:
    """Test OpenAI connector functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.connector = OpenAIConnector(
            api_key="sk-test123",
            model="gpt-3.5-turbo",
            temperature=0.7
        )
    
    def test_connector_initialization(self):
        """Test OpenAI connector initialization."""
        assert self.connector.api_key == "sk-test123"
        assert self.connector.model == "gpt-3.5-turbo"
        assert self.connector.config == {"temperature": 0.7}
        assert self.connector.base_url == "https://api.openai.com/v1"
        assert "Bearer sk-test123" in self.connector.headers["Authorization"]
    
    def test_provider_name(self):
        """Test provider name property."""
        assert self.connector.provider_name == "openai"
    
    def test_get_model_info(self):
        """Test model info retrieval."""
        info = self.connector.get_model_info()
        
        assert info["provider"] == "openai"
        assert info["model"] == "gpt-3.5-turbo"
        assert info["base_url"] == "https://api.openai.com/v1"
        assert info["supports_streaming"] is True
        assert info["max_tokens"] == 4096
        assert info["context_window"] == 4096
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self):
        """Test successful connection test."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Connection successful."}}]
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            result = await self.connector.test_connection()
            
            assert result.status == ConnectionStatus.SUCCESS
            assert "Connection successful" in result.message
            assert result.latency_ms is not None
            assert result.model_info is not None
            assert result.model_info["model"] == "gpt-3.5-turbo"
    
    @pytest.mark.asyncio
    async def test_test_connection_invalid_credentials(self):
        """Test connection test with invalid credentials."""
        mock_response = Mock()
        mock_response.status_code = 401
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            result = await self.connector.test_connection()
            
            assert result.status == ConnectionStatus.INVALID_CREDENTIALS
            assert "Invalid API key" in result.message
    
    @pytest.mark.asyncio
    async def test_test_connection_rate_limited(self):
        """Test connection test with rate limiting."""
        mock_response = Mock()
        mock_response.status_code = 429
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            result = await self.connector.test_connection()
            
            assert result.status == ConnectionStatus.RATE_LIMITED
            assert "Rate limit exceeded" in result.message
    
    @pytest.mark.asyncio
    async def test_test_connection_timeout(self):
        """Test connection test with timeout."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.TimeoutException("Timeout")
            )
            
            result = await self.connector.test_connection()
            
            assert result.status == ConnectionStatus.TIMEOUT
            assert "Connection timeout" in result.message
    
    @pytest.mark.asyncio
    async def test_test_connection_general_error(self):
        """Test connection test with general error."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=Exception("Network error")
            )
            
            result = await self.connector.test_connection()
            
            assert result.status == ConnectionStatus.FAILED
            assert "Connection failed" in result.message
    
    @pytest.mark.asyncio
    async def test_send_prompt_success(self):
        """Test successful prompt sending."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            "id": "chatcmpl-123"
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            response = await self.connector.send_prompt(
                prompt="Test prompt",
                system_message="You are a helpful assistant",
                temperature=0.8,
                max_tokens=100
            )
            
            assert response.content == "Test response"
            assert response.model == "gpt-3.5-turbo"
            assert response.usage == {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
            assert response.latency_ms is not None
            assert response.metadata["finish_reason"] == "stop"
            assert response.metadata["provider"] == "openai"
    
    @pytest.mark.asyncio
    async def test_send_prompt_without_system_message(self):
        """Test prompt sending without system message."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}],
            "usage": {"prompt_tokens": 5, "completion_tokens": 10},
            "id": "chatcmpl-123"
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            response = await self.connector.send_prompt("Test prompt")
            
            assert response.content == "Test response"
            assert response.model == "gpt-3.5-turbo"
    
    @pytest.mark.asyncio
    async def test_send_prompt_api_error(self):
        """Test prompt sending with API error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            with pytest.raises(Exception) as exc_info:
                await self.connector.send_prompt("Test prompt")
            
            assert "API error: 400" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_send_prompt_network_error(self):
        """Test prompt sending with network error."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=Exception("Network error")
            )
            
            with pytest.raises(Exception) as exc_info:
                await self.connector.send_prompt("Test prompt")
            
            assert "Failed to send prompt" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_send_prompt_parameters(self):
        """Test prompt sending with various parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}],
            "usage": {"prompt_tokens": 5, "completion_tokens": 10}
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post
            
            await self.connector.send_prompt(
                prompt="Test prompt",
                system_message="System message",
                temperature=0.5,
                max_tokens=500,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            # Verify the request was made with correct parameters
            call_args = mock_post.call_args
            request_data = call_args[1]["json"]
            
            assert request_data["model"] == "gpt-3.5-turbo"
            assert request_data["temperature"] == 0.5
            assert request_data["max_tokens"] == 500
            assert request_data["top_p"] == 0.9
            assert request_data["frequency_penalty"] == 0.1
            assert request_data["presence_penalty"] == 0.1
            assert len(request_data["messages"]) == 2  # system + user message

