"""
Base connector interface for all model providers.

Defines the standard interface that all model connectors must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum


class ConnectionStatus(Enum):
    """Connection status enumeration."""
    SUCCESS = "success"
    FAILED = "failed"
    INVALID_CREDENTIALS = "invalid_credentials"
    RATE_LIMITED = "rate_limited"
    TIMEOUT = "timeout"


@dataclass
class ConnectionResult:
    """Result of a connection test."""
    status: ConnectionStatus
    message: str
    latency_ms: Optional[float] = None
    model_info: Optional[Dict[str, Any]] = None


@dataclass
class ModelResponse:
    """Standardized model response."""
    content: str
    model: str
    usage: Dict[str, Any]
    latency_ms: float
    metadata: Dict[str, Any]


class BaseConnector(ABC):
    """
    Abstract base class for all model connectors.
    
    Provides a standardized interface for:
    - Testing model connections
    - Sending prompts
    - Handling responses
    - Error management
    """
    
    def __init__(self, api_key: str, model: str, **kwargs):
        """
        Initialize the connector.
        
        Args:
            api_key: API key for the model provider
            model: Model identifier (e.g., "gpt-3.5-turbo")
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.model = model
        self.config = kwargs
    
    @abstractmethod
    async def test_connection(self) -> ConnectionResult:
        """
        Test the connection to the model provider.
        
        Returns:
            ConnectionResult with status and details
        """
        pass
    
    @abstractmethod
    async def send_prompt(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """
        Send a prompt to the model and get response.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            ModelResponse with standardized format
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the connected model.
        
        Returns:
            Dictionary with model metadata
        """
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the provider name (e.g., 'openai', 'anthropic')."""
        pass

