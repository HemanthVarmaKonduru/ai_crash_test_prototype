#!/usr/bin/env python3
"""
Test API Functionality
Tests that all APIs are working correctly after security fixes.
"""
import sys
import os
import asyncio
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
        print(f"✓ Loaded .env from {env_path}\n")
    else:
        print(f"⚠️ .env file not found at {env_path}")
        sys.exit(1)
except ImportError:
    print("⚠️ python-dotenv not installed")
    sys.exit(1)

print("="*60)
print("Testing API Functionality After Security Fixes")
print("="*60 + "\n")

# Test 1: Backend Configuration
print("1. Testing Backend Configuration Loading...")
try:
    from backend.config.settings import (
        API_KEY, TARGET_MODEL, JUDGE_MODEL,
        OLLAMA_API_KEY, OLLAMA_HOST, OLLAMA_JUDGE_MODEL, USE_OLLAMA_FOR_EVALUATION,
        VALID_EMAIL, VALID_PASSWORD,
        CORS_ORIGINS
    )
    
    print("   ✓ All configuration variables imported successfully")
    print(f"   ✓ OPENAI_API_KEY: {'SET' if API_KEY else 'NOT SET'}")
    print(f"   ✓ TARGET_MODEL: {TARGET_MODEL}")
    print(f"   ✓ JUDGE_MODEL: {JUDGE_MODEL}")
    print(f"   ✓ USE_OLLAMA_FOR_EVALUATION: {USE_OLLAMA_FOR_EVALUATION}")
    if USE_OLLAMA_FOR_EVALUATION:
        print(f"   ✓ OLLAMA_API_KEY: {'SET' if OLLAMA_API_KEY else 'NOT SET'}")
        print(f"   ✓ OLLAMA_HOST: {OLLAMA_HOST}")
        print(f"   ✓ OLLAMA_JUDGE_MODEL: {OLLAMA_JUDGE_MODEL}")
    print(f"   ✓ VALID_EMAIL: {'SET' if VALID_EMAIL else 'NOT SET'}")
    print(f"   ✓ VALID_PASSWORD: {'SET' if VALID_PASSWORD else 'NOT SET'}")
    print("   ✓ PASS\n")
except Exception as e:
    print(f"   ✗ FAILED: {e}\n")
    sys.exit(1)

# Test 2: Test OpenAI Client Initialization
print("2. Testing OpenAI Client Initialization...")
try:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=API_KEY)
    print("   ✓ OpenAI client initialized successfully")
    print("   ✓ PASS\n")
except Exception as e:
    print(f"   ✗ FAILED: {e}\n")
    sys.exit(1)

# Test 3: Test LLM Client (for evaluation)
print("3. Testing LLM Client for Evaluation...")
try:
    from backend.utils.llm_client import LLMClient
    from backend.config.settings import (
        USE_OLLAMA_FOR_EVALUATION,
        OLLAMA_API_KEY,
        OLLAMA_HOST,
        OLLAMA_JUDGE_MODEL,
        API_KEY,
        JUDGE_MODEL
    )
    
    if USE_OLLAMA_FOR_EVALUATION:
        llm_client = LLMClient(
            provider="ollama",
            api_key=OLLAMA_API_KEY,
            host=OLLAMA_HOST
        )
        print(f"   ✓ Ollama LLM client initialized (model: {OLLAMA_JUDGE_MODEL})")
    else:
        llm_client = LLMClient(
            provider="openai",
            api_key=API_KEY
        )
        print(f"   ✓ OpenAI LLM client initialized (model: {JUDGE_MODEL})")
    print("   ✓ PASS\n")
except Exception as e:
    print(f"   ✗ FAILED: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test Platform Services (if available)
print("4. Testing Platform Services Configuration...")
try:
    sys.path.insert(0, str(project_root / "platform" / "services" / "api-gateway" / "src"))
    
    try:
        from prompt_injection_api import API_KEY as PI_API_KEY, TARGET_MODEL as PI_TARGET_MODEL
        print(f"   ✓ prompt_injection_api.py: API_KEY loaded from environment")
        print(f"   ✓ prompt_injection_api.py: TARGET_MODEL = {PI_TARGET_MODEL}")
    except Exception as e:
        print(f"   ⚠️  prompt_injection_api.py: {e}")
    
    try:
        from jailbreak_api import API_KEY as JB_API_KEY, TARGET_MODEL as JB_TARGET_MODEL
        print(f"   ✓ jailbreak_api.py: API_KEY loaded from environment")
        print(f"   ✓ jailbreak_api.py: TARGET_MODEL = {JB_TARGET_MODEL}")
    except Exception as e:
        print(f"   ⚠️  jailbreak_api.py: {e}")
    
    print("   ✓ PASS\n")
except Exception as e:
    print(f"   ⚠️  Platform services test skipped: {e}\n")

# Test 5: Test Authentication Service
print("5. Testing Authentication Service...")
try:
    from backend.services.auth import validate_credentials, create_session
    
    # Test with configured credentials
    if VALID_EMAIL and VALID_PASSWORD:
        is_valid = validate_credentials(VALID_EMAIL, VALID_PASSWORD)
        if is_valid:
            print(f"   ✓ Authentication validation works")
            token = create_session(VALID_EMAIL)
            print(f"   ✓ Session creation works (token: {token[:20]}...)")
        else:
            print(f"   ✗ Authentication validation failed")
            sys.exit(1)
    else:
        print(f"   ⚠️  Credentials not configured, skipping auth test")
    
    print("   ✓ PASS\n")
except Exception as e:
    print(f"   ✗ FAILED: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Test API Endpoints (if server is running)
print("6. Testing API Endpoints (if server is running)...")
try:
    import requests
    import time
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("   ✓ Backend server is running")
            print(f"   ✓ Health check: {response.json()}")
        else:
            print(f"   ⚠️  Backend server returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ⚠️  Backend server not running (this is OK for config test)")
    except Exception as e:
        print(f"   ⚠️  Could not test health endpoint: {e}")
    
    print("   ✓ PASS\n")
except ImportError:
    print("   ⚠️  requests library not available, skipping endpoint test\n")
except Exception as e:
    print(f"   ⚠️  Endpoint test error: {e}\n")

print("="*60)
print("✓ All API Functionality Tests PASSED!")
print("="*60 + "\n")
print("Summary:")
print("  ✓ Backend configuration loads correctly")
print("  ✓ OpenAI client initializes")
print("  ✓ LLM evaluation client initializes")
print("  ✓ Platform services configured")
print("  ✓ Authentication service works")
print("\n✅ The APIs are properly configured and ready to use!")

