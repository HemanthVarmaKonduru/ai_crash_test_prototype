#!/usr/bin/env python3
"""
Test script to verify environment variable configuration is working correctly.
This script checks that all required environment variables are set and accessible.
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load .env file
try:
    from dotenv import load_dotenv
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded .env from {env_path}")
    else:
        print(f"⚠️ .env file not found at {env_path}")
        print("   Please create a .env file based on env.example")
        sys.exit(1)
except ImportError:
    print("⚠️ python-dotenv not installed")
    sys.exit(1)

print("\n" + "="*60)
print("Testing Environment Variable Configuration")
print("="*60 + "\n")

# Test that we can import settings (this will validate required vars)
try:
    from backend.config.settings import (
        API_KEY,
        TARGET_MODEL,
        JUDGE_MODEL,
        USE_OLLAMA_FOR_EVALUATION,
        OLLAMA_API_KEY,
        OLLAMA_HOST,
        OLLAMA_JUDGE_MODEL,
        VALID_EMAIL,
        VALID_PASSWORD,
        CORS_ORIGINS
    )
    
    print("✓ Successfully imported all settings from backend.config.settings")
    print("\nConfiguration Values:")
    print(f"  OPENAI_API_KEY: {'✓ Set' if API_KEY else '✗ Missing'}")
    print(f"  TARGET_MODEL: {TARGET_MODEL}")
    print(f"  JUDGE_MODEL: {JUDGE_MODEL}")
    print(f"  USE_OLLAMA_FOR_EVALUATION: {USE_OLLAMA_FOR_EVALUATION}")
    if USE_OLLAMA_FOR_EVALUATION:
        print(f"  OLLAMA_API_KEY: {'✓ Set' if OLLAMA_API_KEY else '✗ Missing'}")
        print(f"  OLLAMA_HOST: {OLLAMA_HOST}")
        print(f"  OLLAMA_JUDGE_MODEL: {OLLAMA_JUDGE_MODEL}")
    print(f"  VALID_EMAIL: {'✓ Set' if VALID_EMAIL else '✗ Missing'}")
    print(f"  VALID_PASSWORD: {'✓ Set' if VALID_PASSWORD else '✗ Missing'}")
    print(f"  CORS_ORIGINS: {CORS_ORIGINS}")
    
    print("\n" + "="*60)
    print("✓ All environment variables are properly configured!")
    print("="*60 + "\n")
    
except ValueError as e:
    print(f"\n✗ Configuration Error: {e}")
    print("\nPlease ensure your .env file contains all required variables.")
    print("See env.example for reference.")
    sys.exit(1)
except Exception as e:
    print(f"\n✗ Unexpected Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

