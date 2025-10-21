"""
Connectors Library - Model Provider Adapters

This module provides standardized interfaces for connecting to various LLM providers.
Each connector implements a common interface for model testing, API calls, and response normalization.
"""

from .base import BaseConnector, ConnectionResult, ModelResponse
from .openai_connector import OpenAIConnector

__all__ = [
    "BaseConnector",
    "ConnectionResult", 
    "ModelResponse",
    "OpenAIConnector"
]

