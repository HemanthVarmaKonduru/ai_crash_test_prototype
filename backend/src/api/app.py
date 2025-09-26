"""
FastAPI application factory
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .v1 import api_v1
from ..config import ConfigManager


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # Create FastAPI app
    app = FastAPI(
        title=config.app_name,
        description="Modular AI Crash Test Prototype API",
        version=config.version,
        debug=config.debug
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_v1, prefix="/api/v1")
    
    # Add configuration to app state
    app.state.config = config
    app.state.config_manager = config_manager
    
    return app


