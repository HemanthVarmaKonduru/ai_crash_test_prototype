#!/usr/bin/env python3
"""
Startup script for backend API server.
Run this from the project root directory.
"""
import sys
import os
import uvicorn
from pathlib import Path

# Ensure we're running from project root
if __name__ == "__main__":
    # Add project root to path
    project_root = os.path.abspath(os.path.dirname(__file__) + '/..')
    sys.path.insert(0, project_root)
    
    # Load .env file if it exists (settings.py will also try to load it)
    try:
        from dotenv import load_dotenv
        env_path = Path(project_root) / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            print(f"✓ Loaded .env from {env_path}")
    except ImportError:
        pass  # python-dotenv not installed, will use environment variables only
    
    # Run the API server
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )



