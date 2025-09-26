"""
Configuration models
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class LogLevel(str, Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ModelConfig(BaseModel):
    """Model configuration"""
    name: str
    provider: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 200
    temperature: float = 0.7
    timeout: int = 30
    retry_attempts: int = 3
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EvaluationConfig(BaseModel):
    """Evaluation configuration"""
    evaluator_name: str
    strict_mode: bool = False
    custom_rules: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AppConfig(BaseModel):
    """Application configuration"""
    app_name: str = "AI Crash Test Prototype"
    version: str = "2.0.0"
    debug: bool = False
    log_level: LogLevel = LogLevel.INFO
    
    # Model configurations
    models: Dict[str, ModelConfig] = Field(default_factory=dict)
    
    # Evaluation configurations
    evaluation: EvaluationConfig = Field(default_factory=lambda: EvaluationConfig(evaluator_name="default"))
    
    # Data paths
    data_dir: str = "data"
    output_dir: str = "output"
    cache_dir: str = "cache"
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    
    # Database settings
    database_url: str = "sqlite:///./ai_crash_test.db"
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


