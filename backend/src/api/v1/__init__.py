"""
API v1 routes
"""
from fastapi import APIRouter
from .endpoints import testing, models, datasets, health

api_v1 = APIRouter()

# Include endpoint routers
api_v1.include_router(health.router, prefix="/health", tags=["health"])
api_v1.include_router(models.router, prefix="/models", tags=["models"])
api_v1.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_v1.include_router(testing.router, prefix="/testing", tags=["testing"])


