"""
Model pricing configuration for cost calculation.
Based on OpenAI and Ollama Cloud pricing as of 2024.
"""
from typing import Dict, Optional

# Pricing per 1M tokens (in USD)
# Format: {model_name: {"input": price_per_1M, "output": price_per_1M}}
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    # OpenAI Models
    "gpt-3.5-turbo": {
        "input": 0.50 / 1_000_000,  # $0.50 per 1M tokens
        "output": 1.50 / 1_000_000,  # $1.50 per 1M tokens
    },
    "gpt-3.5-turbo-0125": {
        "input": 0.50 / 1_000_000,
        "output": 1.50 / 1_000_000,
    },
    "gpt-3.5-turbo-1106": {
        "input": 0.50 / 1_000_000,
        "output": 1.50 / 1_000_000,
    },
    "gpt-4": {
        "input": 30.00 / 1_000_000,  # $30 per 1M tokens
        "output": 60.00 / 1_000_000,  # $60 per 1M tokens
    },
    "gpt-4-turbo": {
        "input": 10.00 / 1_000_000,  # $10 per 1M tokens
        "output": 30.00 / 1_000_000,  # $30 per 1M tokens
    },
    "gpt-4o": {
        "input": 2.50 / 1_000_000,  # $2.50 per 1M tokens
        "output": 10.00 / 1_000_000,  # $10 per 1M tokens
    },
    "gpt-4o-mini": {
        "input": 0.15 / 1_000_000,  # $0.15 per 1M tokens
        "output": 0.60 / 1_000_000,  # $0.60 per 1M tokens
    },
    # Ollama Cloud Models (approximate pricing - may vary)
    "glm-4.6:cloud": {
        "input": 0.20 / 1_000_000,  # Estimated
        "output": 0.80 / 1_000_000,  # Estimated
    },
    "gpt-oss:20b-cloud": {
        "input": 0.10 / 1_000_000,  # Estimated
        "output": 0.40 / 1_000_000,  # Estimated
    },
    # Default fallback for unknown models
    "default": {
        "input": 1.00 / 1_000_000,  # Conservative estimate
        "output": 2.00 / 1_000_000,
    },
}


class ModelPricing:
    """Handles model pricing lookups and cost calculations."""
    
    @staticmethod
    def get_pricing(model_name: str) -> Dict[str, float]:
        """
        Get pricing for a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary with 'input' and 'output' prices per token
        """
        # Try exact match first
        if model_name in MODEL_PRICING:
            return MODEL_PRICING[model_name]
        
        # Try partial matches (e.g., "gpt-3.5-turbo-0125" matches "gpt-3.5-turbo")
        for key in MODEL_PRICING.keys():
            if key != "default" and model_name.startswith(key.split("-")[0]):
                # Try to match base model name
                base_name = "-".join(model_name.split("-")[:2])  # e.g., "gpt-3.5" -> "gpt-3.5-turbo"
                if base_name in key or key in model_name:
                    return MODEL_PRICING[key]
        
        # Return default pricing
        return MODEL_PRICING["default"]
    
    @staticmethod
    def calculate_cost(
        model_name: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Calculate cost for API call.
        
        Args:
            model_name: Name of the model
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Total cost in USD
        """
        pricing = ModelPricing.get_pricing(model_name)
        
        input_cost = input_tokens * pricing["input"]
        output_cost = output_tokens * pricing["output"]
        
        return input_cost + output_cost


def get_model_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    """
    Convenience function to calculate model cost.
    
    Args:
        model_name: Name of the model
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        
    Returns:
        Total cost in USD
    """
    return ModelPricing.calculate_cost(model_name, input_tokens, output_tokens)

