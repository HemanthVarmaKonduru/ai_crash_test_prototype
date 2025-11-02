#!/usr/bin/env python3
"""
Startup script for backend API server.
Run this from the project root directory.
"""
import sys
import os
import uvicorn

# Ensure we're running from project root
if __name__ == "__main__":
    # Add project root to path
    project_root = os.path.abspath(os.path.dirname(__file__) + '/..')
    sys.path.insert(0, project_root)
    
    # Run the API server
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )



