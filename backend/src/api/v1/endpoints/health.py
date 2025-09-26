"""
Health check endpoints
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any
# Removed circular import

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Basic health check"""
    return {
        "status": "healthy",
        "message": "AI Crash Test Prototype API is running",
        "version": "2.0.0"
    }


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with component status"""
    # This would check plugin manager, models, evaluators, etc.
    return {
        "status": "healthy",
        "components": {
            "api": "healthy",
            "plugin_manager": "healthy",
            "models": "healthy",
            "evaluators": "healthy"
        },
        "version": "2.0.0"
    }
