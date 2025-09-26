"""
Dataset management endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from ....plugins import PluginManager

router = APIRouter()


@router.get("/")
async def list_datasets() -> Dict[str, List[str]]:
    """List available dataset plugins"""
    plugin_manager = PluginManager()
    return plugin_manager.list_plugins("dataset")


@router.get("/{dataset_name}")
async def get_dataset_info(dataset_name: str) -> Dict[str, Any]:
    """Get dataset information"""
    plugin_manager = PluginManager()
    plugin_info = plugin_manager.get_plugin_info("dataset", dataset_name)
    
    if not plugin_info:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_name}' not found")
    
    return {
        "name": dataset_name,
        "type": "dataset",
        "class": plugin_info["class"].__name__,
        "config_schema": plugin_info.get("config_schema", {})
    }


@router.post("/{dataset_name}/load")
async def load_dataset(
    dataset_name: str, 
    limit: int = 10,
    filters: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Load a dataset with optional filtering"""
    try:
        plugin_manager = PluginManager()
        # This would require proper dataset plugin implementation
        return {
            "dataset": dataset_name,
            "limit": limit,
            "filters": filters or {},
            "status": "load_not_implemented",
            "message": "Dataset loading requires proper plugin implementation"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


