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
    # Get the directory where this script is located (backend/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Project root is one level up from backend/
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    
    # Change to project root directory
    os.chdir(project_root)
    
    # Add project root to path
    sys.path.insert(0, project_root)
    
    # Load .env file if it exists
    try:
        from dotenv import load_dotenv
        env_path = Path(project_root) / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            print(f"✓ Loaded .env from {env_path}")
    except ImportError:
        pass
    
    # Import the app directly (this ensures path is set)
    from backend.api.main import app
    
    # Get port from Railway environment variable
    port = int(os.getenv("PORT", 8000))
    print(f"✓ Starting server on port {port}")
    
    # Run the API server
    uvicorn.run(
        app,  # Pass the app object directly instead of string
        host="0.0.0.0",
        port=port,
        reload=False
    )