"""
OpenAI API connector implementation.

Handles connection to OpenAI's GPT models with standardized interface.
"""

import asyncio
import time
from typing import Dict, Any, Optional
import httpx
from .base import BaseConnector, ConnectionResult, ModelResponse, ConnectionStatus


class OpenAIConnector(BaseConnector):
    """OpenAI API connector for GPT models."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", **kwargs):
        """
        Initialize OpenAI connector.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-3.5-turbo)
            **kwargs: Additional OpenAI parameters
        """
        super().__init__(api_key, model, **kwargs)
        self.base_url = "https://api.openai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "openai"
    
    async def test_connection(self) -> ConnectionResult:
        """
        Test connection to OpenAI API.
        
        Returns:
            ConnectionResult with test results
        """
        start_time = time.time()
        
        try:
            # Simple test prompt to verify connection
            test_prompt = "Hello, this is a connection test. Please respond with 'Connection successful.'"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": test_prompt}],
                        "max_tokens": 50,
                        "temperature": 0.1
                    }
                )
                
                latency_ms = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    return ConnectionResult(
                        status=ConnectionStatus.SUCCESS,
                        message="Connection successful",
                        latency_ms=latency_ms,
                        model_info={
                            "model": self.model,
                            "provider": self.provider_name,
                            "response": data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        }
                    )
                elif response.status_code == 401:
                    return ConnectionResult(
                        status=ConnectionStatus.INVALID_CREDENTIALS,
                        message="Invalid API key"
                    )
                elif response.status_code == 429:
                    return ConnectionResult(
                        status=ConnectionStatus.RATE_LIMITED,
                        message="Rate limit exceeded"
                    )
                else:
                    return ConnectionResult(
                        status=ConnectionStatus.FAILED,
                        message=f"API error: {response.status_code}"
                    )
                    
        except httpx.TimeoutException:
            return ConnectionResult(
                status=ConnectionStatus.TIMEOUT,
                message="Connection timeout"
            )
        except Exception as e:
            return ConnectionResult(
                status=ConnectionStatus.FAILED,
                message=f"Connection failed: {str(e)}"
            )
    
    async def send_prompt(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """
        Send prompt to OpenAI model.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            ModelResponse with standardized format
        """
        start_time = time.time()
        
        # Build messages array
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        # Default parameters
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
            "top_p": kwargs.get("top_p", 1.0),
            "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
            "presence_penalty": kwargs.get("presence_penalty", 0.0)
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=params
                )
                
                latency_ms = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    choice = data.get("choices", [{}])[0]
                    content = choice.get("message", {}).get("content", "")
                    usage = data.get("usage", {})
                    
                    return ModelResponse(
                        content=content,
                        model=self.model,
                        usage=usage,
                        latency_ms=latency_ms,
                        metadata={
                            "finish_reason": choice.get("finish_reason"),
                            "provider": self.provider_name,
                            "response_id": data.get("id")
                        }
                    )
                else:
                    raise Exception(f"API error: {response.status_code} - {response.text}")
                    
        except Exception as e:
            raise Exception(f"Failed to send prompt: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the OpenAI model.
        
        Returns:
            Dictionary with model metadata
        """
        return {
            "provider": self.provider_name,
            "model": self.model,
            "base_url": self.base_url,
            "supports_streaming": True,
            "max_tokens": 4096,  # GPT-3.5-turbo limit
            "context_window": 4096
        }

