"""
Plugin registry for storing plugin metadata
"""
from typing import Dict, Any, Type, Optional, List
from ..interfaces.model_interface import ModelInterface
from ..interfaces.evaluator_interface import EvaluatorInterface
from ..interfaces.dataset_interface import DatasetInterface
from ..interfaces.storage_interface import StorageInterface


class PluginRegistry:
    """Registry for managing plugin metadata"""
    
    def __init__(self):
        self._plugins: Dict[str, Dict[str, Dict[str, Any]]] = {
            "model": {},
            "evaluator": {},
            "dataset": {},
            "storage": {}
        }
    
    def register_plugin(
        self, 
        plugin_type: str, 
        name: str, 
        plugin_class: Type,
        config_schema: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a plugin"""
        if plugin_type not in self._plugins:
            raise ValueError(f"Unknown plugin type: {plugin_type}")
        
        self._plugins[plugin_type][name] = {
            "class": plugin_class,
            "config_schema": config_schema or {},
            "name": name,
            "type": plugin_type
        }
    
    def get_plugin(self, plugin_type: str, name: str) -> Optional[Dict[str, Any]]:
        """Get plugin information"""
        if plugin_type not in self._plugins:
            return None
        return self._plugins[plugin_type].get(name)
    
    def list_plugins(self, plugin_type: Optional[str] = None) -> Dict[str, List[str]]:
        """List available plugins"""
        if plugin_type:
            if plugin_type in self._plugins:
                return {plugin_type: list(self._plugins[plugin_type].keys())}
            return {plugin_type: []}
        
        return {
            plugin_type: list(plugins.keys()) 
            for plugin_type, plugins in self._plugins.items()
        }
    
    def unregister_plugin(self, plugin_type: str, name: str) -> bool:
        """Unregister a plugin"""
        if plugin_type not in self._plugins:
            return False
        
        if name in self._plugins[plugin_type]:
            del self._plugins[plugin_type][name]
            return True
        return False
    
    def get_all_plugins(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Get all registered plugins"""
        return self._plugins.copy()


