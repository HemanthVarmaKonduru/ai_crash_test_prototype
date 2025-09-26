"""
Model management endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from ....models.config import ModelConfig
from ....plugins import PluginManager

router = APIRouter()


@router.get("/")
async def list_models() -> Dict[str, List[str]]:
    """List available model plugins"""
    plugin_manager = PluginManager()
    return plugin_manager.list_plugins("model")


@router.get("/{model_name}")
async def get_model_info(model_name: str) -> Dict[str, Any]:
    """Get model information"""
    plugin_manager = PluginManager()
    plugin_info = plugin_manager.get_plugin_info("model", model_name)
    
    if not plugin_info:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    
    return {
        "name": model_name,
        "type": "model",
        "class": plugin_info["class"].__name__,
        "config_schema": plugin_info.get("config_schema", {})
    }


@router.post("/{model_name}/test")
async def test_model(model_name: str, test_prompt: str = "Hello, how are you?") -> Dict[str, Any]:
    """Test a model with a simple prompt"""
    try:
        plugin_manager = PluginManager()
        # This would require proper config loading
        # For now, return a placeholder
        return {
            "model": model_name,
            "test_prompt": test_prompt,
            "status": "test_not_implemented",
            "message": "Model testing requires proper configuration"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


