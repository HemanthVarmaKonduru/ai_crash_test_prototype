#!/usr/bin/env python3
"""
Main application entry point for the new modular architecture
"""
import uvicorn
from src.api.app import create_app

if __name__ == "__main__":
    uvicorn.run(
        "main_v2:app", 
        host="0.0.0.0", 
        port=8000,
        reload=True
    )

# Create app instance for uvicorn
app = create_app()
