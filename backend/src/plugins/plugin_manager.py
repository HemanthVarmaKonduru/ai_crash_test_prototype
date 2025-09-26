"""
Plugin manager for dynamic loading and management
"""
from typing import Dict, Any, Type, Optional, List
from src.interfaces.model_interface import ModelInterface
from src.interfaces.evaluator_interface import EvaluatorInterface
from src.interfaces.dataset_interface import DatasetInterface
from src.interfaces.storage_interface import StorageInterface
from .registry import PluginRegistry


class PluginManager:
    """Manages plugin loading and instantiation"""
    
    def __init__(self):
        self.registry = PluginRegistry()
        self._loaded_plugins: Dict[str, Any] = {}
    
    def register_model(
        self, 
        name: str, 
        plugin_class: Type[ModelInterface],
        config_schema: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a model plugin"""
        self.registry.register_plugin(
            "model", name, plugin_class, config_schema
        )
    
    def register_evaluator(
        self, 
        name: str, 
        plugin_class: Type[EvaluatorInterface],
        config_schema: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register an evaluator plugin"""
        self.registry.register_plugin(
            "evaluator", name, plugin_class, config_schema
        )
    
    def register_dataset(
        self, 
        name: str, 
        plugin_class: Type[DatasetInterface],
        config_schema: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a dataset plugin"""
        self.registry.register_plugin(
            "dataset", name, plugin_class, config_schema
        )
    
    def register_storage(
        self, 
        name: str, 
        plugin_class: Type[StorageInterface],
        config_schema: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a storage plugin"""
        self.registry.register_plugin(
            "storage", name, plugin_class, config_schema
        )
    
    def create_model(self, name: str, config: Dict[str, Any]) -> ModelInterface:
        """Create a model instance"""
        plugin_info = self.registry.get_plugin("model", name)
        if not plugin_info:
            raise ValueError(f"Model plugin '{name}' not found")
        
        plugin_class = plugin_info["class"]
        
        # Convert dict to ModelConfig if needed
        if hasattr(plugin_class, '__init__'):
            import inspect
            sig = inspect.signature(plugin_class.__init__)
            params = list(sig.parameters.keys())
            if len(params) > 1 and params[1] == 'config':
                # Check if the second parameter expects ModelConfig
                param_type = sig.parameters['config'].annotation
                if hasattr(param_type, '__name__') and 'ModelConfig' in str(param_type):
                    from src.models.config import ModelConfig
                    config = ModelConfig(**config)
        
        return plugin_class(config)
    
    def create_evaluator(self, name: str, config: Dict[str, Any]) -> EvaluatorInterface:
        """Create an evaluator instance"""
        plugin_info = self.registry.get_plugin("evaluator", name)
        if not plugin_info:
            raise ValueError(f"Evaluator plugin '{name}' not found")
        
        plugin_class = plugin_info["class"]
        
        # Convert dict to EvaluationConfig if needed
        if hasattr(plugin_class, '__init__'):
            import inspect
            sig = inspect.signature(plugin_class.__init__)
            params = list(sig.parameters.keys())
            if len(params) > 1 and params[1] == 'config':
                # Check if the second parameter expects EvaluationConfig
                param_type = sig.parameters['config'].annotation
                if hasattr(param_type, '__name__') and 'EvaluationConfig' in str(param_type):
                    from src.models.config import EvaluationConfig
                    config = EvaluationConfig(**config)
        
        return plugin_class(config)
    
    def create_dataset(self, name: str, config: Dict[str, Any]) -> DatasetInterface:
        """Create a dataset instance"""
        plugin_info = self.registry.get_plugin("dataset", name)
        if not plugin_info:
            raise ValueError(f"Dataset plugin '{name}' not found")
        
        plugin_class = plugin_info["class"]
        return plugin_class(config)
    
    def create_storage(self, name: str, config: Dict[str, Any]) -> StorageInterface:
        """Create a storage instance"""
        plugin_info = self.registry.get_plugin("storage", name)
        if not plugin_info:
            raise ValueError(f"Storage plugin '{name}' not found")
        
        plugin_class = plugin_info["class"]
        return plugin_class(config)
    
    def list_plugins(self, plugin_type: Optional[str] = None) -> Dict[str, List[str]]:
        """List available plugins"""
        return self.registry.list_plugins(plugin_type)
    
    def get_plugin_info(self, plugin_type: str, name: str) -> Optional[Dict[str, Any]]:
        """Get plugin information"""
        return self.registry.get_plugin(plugin_type, name)