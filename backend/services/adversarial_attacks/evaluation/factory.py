"""
Factory functions for creating evaluator instances.

Provides convenient factory functions for initializing the evaluator
with proper defaults and configurations.
"""
from typing import Optional
from .evaluator import AdversarialAttacksEvaluator
from .config import EvaluationConfig, DEFAULT_CONFIG


def create_evaluator(
    use_openai_embeddings: bool = False,
    config: Optional[EvaluationConfig] = None
) -> AdversarialAttacksEvaluator:
    """
    Factory function to create an AdversarialAttacksEvaluator instance.
    
    Args:
        use_openai_embeddings: Whether to use OpenAI embeddings (default: False, uses local)
        config: Optional custom configuration (default: uses DEFAULT_CONFIG)
        
    Returns:
        Configured AdversarialAttacksEvaluator instance
        
    Example:
        ```python
        evaluator = create_evaluator()
        await evaluator.initialize()
        result = await evaluator.evaluate(context)
        ```
    """
    if config is None:
        config = EvaluationConfig.from_env()
        config.use_openai_embeddings = use_openai_embeddings
    else:
        config.use_openai_embeddings = use_openai_embeddings
    
    return AdversarialAttacksEvaluator(config=config)


def create_evaluator_with_defaults() -> AdversarialAttacksEvaluator:
    """
    Create evaluator with default configuration.
    
    Uses local embeddings (sentence-transformers) by default.
    
    Returns:
        AdversarialAttacksEvaluator with default settings
    """
    return create_evaluator(use_openai_embeddings=False)

