"""
OpenAI model implementation
"""
import asyncio
from typing import Dict, Any
from openai import AsyncOpenAI
from src.interfaces.model_interface import ModelInterface
from src.models.prompt import Prompt
from src.models.config import ModelConfig


class OpenAIModel(ModelInterface):
    """OpenAI model implementation"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response for the given prompt"""
        try:
            response = await self.client.chat.completions.create(
                model=self.name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
                timeout=kwargs.get("timeout", self.config.timeout)
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def test_prompt(self, prompt: Prompt, **kwargs) -> str:
        """Test a single prompt and return the response"""
        return await self.generate_response(prompt.content, **kwargs)
    
    async def health_check(self) -> bool:
        """Check if the model is available and healthy"""
        try:
            response = await self.client.chat.completions.create(
                model=self.name,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=1,
                timeout=5
            )
            return response.choices[0].message.content is not None
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and capabilities"""
        return {
            "name": self.name,
            "provider": self.provider,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "supports_streaming": True,
            "supports_functions": True
        }