"""
LLM Client wrapper to support multiple providers (OpenAI, Ollama Cloud).
"""
import os
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI


class LLMClient:
    """Unified async client for LLM inference supporting OpenAI and Ollama Cloud."""
    
    def __init__(self, provider: str = "openai", api_key: Optional[str] = None, host: Optional[str] = None):
        """
        Initialize LLM client.
        
        Args:
            provider: "openai" or "ollama"
            api_key: API key for the provider
            host: API host URL (for Ollama Cloud)
        """
        self.provider = provider.lower()
        
        if self.provider == "openai":
            self.client = AsyncOpenAI(api_key=api_key)
        elif self.provider == "ollama":
            # Ollama uses OpenAI-compatible API
            self.client = AsyncOpenAI(
                base_url=f"{host}/v1" if host else "https://ollama.com/v1",
                api_key=api_key
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Get chat completion from the LLM (async).
        
        Args:
            model: Model name
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Response content as string
        """
        try:
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature
            }
            
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            
            response = await self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"LLM API error ({self.provider}): {str(e)}")
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider."""
        return {
            "provider": self.provider,
            "client_type": type(self.client).__name__
        }

