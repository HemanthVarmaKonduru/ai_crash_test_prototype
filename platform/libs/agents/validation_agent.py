"""
Validation Agent for validating user inputs and API credentials.
"""

import re
import httpx
from typing import Dict, Any
from base_agent import BaseAgent, AgentResult

class ValidationAgent(BaseAgent):
    """Agent responsible for validating user inputs and API credentials."""
    
    def __init__(self, config: Dict[str, Any], agent_id: str = "validation_agent"):
        super().__init__(config, agent_id)
        self.openai_api_key_pattern = re.compile(r'^sk-[a-zA-Z0-9]{48}$')
        
    async def execute(self, state: Dict[str, Any]) -> AgentResult:
        """
        Validate user inputs and API credentials.
        
        Args:
            state: Workflow state containing user inputs
            
        Returns:
            AgentResult: Validation result
        """
        try:
            await self.pre_execute(state)
            
            # Extract validation data from state
            api_key = state.get("api_key")
            model = state.get("model")
            user_id = state.get("user_id")
            
            # Validate API key format
            if not self._validate_api_key(api_key):
                return AgentResult(
                    success=False,
                    data={},
                    error="Invalid API key format",
                    confidence=0.0
                )
            
            # Validate model name
            if not self._validate_model(model):
                return AgentResult(
                    success=False,
                    data={},
                    error="Invalid model name",
                    confidence=0.0
                )
            
            # Test API connection
            connection_valid = await self._test_api_connection(api_key, model)
            if not connection_valid:
                return AgentResult(
                    success=False,
                    data={},
                    error="API connection failed",
                    confidence=0.0
                )
            
            # Prepare validation result
            result_data = {
                "api_key_valid": True,
                "model_valid": True,
                "connection_valid": True,
                "user_id": user_id,
                "model": model
            }
            
            result = AgentResult(
                success=True,
                data=result_data,
                confidence=1.0,
                metadata={"validation_type": "api_credentials"}
            )
            
            return await self.post_execute(result)
            
        except Exception as e:
            return await self.handle_error(e)
    
    async def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data structure.
        
        Args:
            data: Input data to validate
            
        Returns:
            bool: True if valid structure
        """
        required_fields = ["api_key", "model", "user_id"]
        return all(field in data for field in required_fields)
    
    def _validate_api_key(self, api_key: str) -> bool:
        """Validate OpenAI API key format."""
        if not api_key:
            return False
        return bool(self.openai_api_key_pattern.match(api_key))
    
    def _validate_model(self, model: str) -> bool:
        """Validate model name."""
        if not model:
            return False
        
        # Common OpenAI models
        valid_models = [
            "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-turbo",
            "gpt-4o", "gpt-4o-mini", "gpt-4.1-mini"
        ]
        
        return model.lower() in [m.lower() for m in valid_models]
    
    async def _test_api_connection(self, api_key: str, model: str) -> bool:
        """Test API connection with provided credentials."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 5
                    },
                    timeout=10.0
                )
                return response.status_code == 200
        except Exception:
            return False
