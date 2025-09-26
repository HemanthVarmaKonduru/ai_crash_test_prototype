"""
Model interface for AI model providers
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..models.prompt import Prompt
from ..models.config import ModelConfig


class ModelInterface(ABC):
    """Abstract interface for AI model providers"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.name = config.name
        self.provider = config.provider
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response for the given prompt"""
        pass
    
    @abstractmethod
    async def test_prompt(self, prompt: Prompt, **kwargs) -> str:
        """Test a single prompt and return the response"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the model is available and healthy"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and capabilities"""
        pass
    
    def validate_config(self) -> bool:
        """Validate the model configuration"""
        return (
            self.config.name is not None and
            self.config.provider is not None and
            (self.config.api_key is not None or self.config.base_url is not None)
        )


