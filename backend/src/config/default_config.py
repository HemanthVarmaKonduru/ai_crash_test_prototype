"""
Default configuration
"""
from src.models.config import AppConfig, ModelConfig, EvaluationConfig


def get_default_config() -> AppConfig:
    """Get default application configuration"""
    return AppConfig(
        app_name="AI Crash Test Prototype",
        version="2.0.0",
        debug=False,
        models={
            "openai": ModelConfig(
                name="gpt-3.5-turbo",
                provider="openai",
                max_tokens=200,
                temperature=0.7
            )
        },
        evaluation=EvaluationConfig(
            evaluator_name="safety",
            strict_mode=False
        )
    )
