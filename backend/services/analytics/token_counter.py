"""
Token counting utilities for analytics.
"""
from typing import Dict, Any, Optional
from openai.types.chat import ChatCompletion


def extract_token_usage(response: Any) -> Dict[str, int]:
    """
    Extract token usage from OpenAI API response.
    
    Args:
        response: OpenAI ChatCompletion response object
        
    Returns:
        Dictionary with input_tokens, output_tokens, total_tokens
    """
    try:
        if hasattr(response, 'usage') and response.usage:
            usage = response.usage
            return {
                "input_tokens": getattr(usage, 'prompt_tokens', 0) or 0,
                "output_tokens": getattr(usage, 'completion_tokens', 0) or 0,
                "total_tokens": getattr(usage, 'total_tokens', 0) or 0,
            }
        elif isinstance(response, dict) and 'usage' in response:
            usage = response['usage']
            return {
                "input_tokens": usage.get('prompt_tokens', 0) or 0,
                "output_tokens": usage.get('completion_tokens', 0) or 0,
                "total_tokens": usage.get('total_tokens', 0) or 0,
            }
    except Exception as e:
        print(f"Warning: Could not extract token usage: {e}")
    
    # Return zeros if extraction fails
    return {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
    }


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text (rough approximation).
    Uses rule of thumb: ~4 characters per token for English text.
    
    Args:
        text: Text to estimate tokens for
        
    Returns:
        Estimated token count
    """
    if not text:
        return 0
    # Rough approximation: 1 token ≈ 4 characters for English
    return len(text) // 4


def aggregate_token_usage(token_records: list) -> Dict[str, int]:
    """
    Aggregate token usage from multiple API calls.
    
    Args:
        token_records: List of token usage dictionaries
        
    Returns:
        Aggregated token counts
    """
    total_input = sum(record.get("input_tokens", 0) for record in token_records)
    total_output = sum(record.get("output_tokens", 0) for record in token_records)
    total = sum(record.get("total_tokens", 0) for record in token_records)
    
    return {
        "input_tokens": total_input,
        "output_tokens": total_output,
        "total_tokens": total,
    }

