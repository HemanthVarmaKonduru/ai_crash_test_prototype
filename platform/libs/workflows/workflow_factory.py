"""
Workflow Factory for creating module-specific workflows.
"""

from typing import Dict, Any, Type
from .base_workflow import BaseWorkflow

class WorkflowFactory:
    """Factory for creating module-specific workflows."""
    
    _workflow_registry = {}
    
    @classmethod
    def register_workflow(cls, module_type: str, workflow_class: Type[BaseWorkflow]):
        """Register a workflow class for a module type."""
        cls._workflow_registry[module_type] = workflow_class
    
    @classmethod
    def create_workflow(cls, module_type: str, config: Dict[str, Any], workflow_id: str) -> BaseWorkflow:
        """
        Create a workflow instance for the specified module type.
        
        Args:
            module_type: Type of module (e.g., 'prompt_injection', 'jailbreak')
            config: Workflow configuration
            workflow_id: Unique workflow identifier
            
        Returns:
            BaseWorkflow: Configured workflow instance
            
        Raises:
            ValueError: If module type is not registered
        """
        if module_type not in cls._workflow_registry:
            raise ValueError(f"Unknown module type: {module_type}")
        
        workflow_class = cls._workflow_registry[module_type]
        return workflow_class(config, workflow_id)
    
    @classmethod
    def get_supported_modules(cls) -> list:
        """Get list of supported module types."""
        return list(cls._workflow_registry.keys())
    
    @classmethod
    def is_module_supported(cls, module_type: str) -> bool:
        """Check if a module type is supported."""
        return module_type in cls._workflow_registry

