"""
Configuration manager
"""
import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from src.models.config import AppConfig, ModelConfig, EvaluationConfig


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config.yaml"
        self._config: Optional[AppConfig] = None
    
    def load_config(self) -> AppConfig:
        """Load configuration from file or environment"""
        if self._config is not None:
            return self._config
        
        # Try to load from file
        if os.path.exists(self.config_path):
            self._config = self._load_from_file()
        else:
            # Load from environment or use defaults
            self._config = self._load_from_environment()
        
        return self._config
    
    def _load_from_file(self) -> AppConfig:
        """Load configuration from YAML file"""
        with open(self.config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        return AppConfig(**config_data)
    
    def _load_from_environment(self) -> AppConfig:
        """Load configuration from environment variables"""
        config_data = {
            "app_name": os.getenv("APP_NAME", "AI Crash Test Prototype"),
            "version": os.getenv("APP_VERSION", "2.0.0"),
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "api_host": os.getenv("API_HOST", "0.0.0.0"),
            "api_port": int(os.getenv("API_PORT", "8000")),
            "database_url": os.getenv("DATABASE_URL", "sqlite:///./ai_crash_test.db"),
            "data_dir": os.getenv("DATA_DIR", "data"),
            "output_dir": os.getenv("OUTPUT_DIR", "output"),
            "cache_dir": os.getenv("CACHE_DIR", "cache"),
        }
        
        # Load model configurations
        models = {}
        if os.getenv("OPENAI_API_KEY"):
            models["openai"] = ModelConfig(
                name=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                provider="openai",
                api_key=os.getenv("OPENAI_API_KEY"),
                max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "200")),
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
            )
        
        config_data["models"] = models
        
        # Load evaluation configuration
        config_data["evaluation"] = EvaluationConfig(
            evaluator_name=os.getenv("EVALUATOR_NAME", "safety"),
            strict_mode=os.getenv("EVALUATOR_STRICT", "false").lower() == "true"
        )
        
        return AppConfig(**config_data)
    
    def save_config(self, config: AppConfig) -> None:
        """Save configuration to file"""
        config_dict = config.dict()
        
        # Create directory if it doesn't exist
        config_dir = Path(self.config_path).parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)
    
    def get_model_config(self, model_name: str) -> Optional[ModelConfig]:
        """Get configuration for a specific model"""
        config = self.load_config()
        return config.models.get(model_name)
    
    def get_evaluation_config(self) -> EvaluationConfig:
        """Get evaluation configuration"""
        config = self.load_config()
        return config.evaluation
    
    def reload_config(self) -> AppConfig:
        """Reload configuration from source"""
        self._config = None
        return self.load_config()
