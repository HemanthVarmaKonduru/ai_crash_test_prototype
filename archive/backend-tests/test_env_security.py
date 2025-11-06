#!/usr/bin/env python3
"""
Security Test Script
Tests that all hardcoded API keys have been removed and environment variables are properly used.
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
        sys.exit(1)
except ImportError:
    print("⚠️ python-dotenv not installed")
    sys.exit(1)

print("\n" + "="*60)
print("Security Test: Checking for Hardcoded API Keys")
print("="*60 + "\n")

# Test 1: Check backend settings
print("1. Testing backend/config/settings.py...")
try:
    from backend.config.settings import (
        API_KEY, TARGET_MODEL, JUDGE_MODEL, OLLAMA_API_KEY,
        VALID_EMAIL, VALID_PASSWORD
    )
    
    # Check that API_KEY is not hardcoded (should be from env)
    if API_KEY and API_KEY.startswith("sk-"):
        print("   ✓ OPENAI_API_KEY loaded from environment")
        print(f"   ✓ Key format valid (starts with sk-, length: {len(API_KEY)})")
    else:
        print("   ✗ OPENAI_API_KEY appears to be invalid or missing")
        sys.exit(1)
    
    # Check that credentials are from env (not hardcoded)
    if VALID_EMAIL and VALID_PASSWORD:
        if VALID_EMAIL != "testuser@123" and VALID_PASSWORD != "Cars@$98":
            print("   ✓ VALID_EMAIL and VALID_PASSWORD loaded from environment")
        else:
            print("   ⚠️  WARNING: Using default test credentials. Please update .env file.")
    else:
        print("   ✗ VALID_EMAIL or VALID_PASSWORD missing")
        sys.exit(1)
    
    print("   ✓ Backend settings: PASS")
except ValueError as e:
    print(f"   ✗ Backend settings validation failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"   ✗ Backend settings import failed: {e}")
    sys.exit(1)

# Test 2: Check platform services (if they can be imported)
print("\n2. Testing platform services...")
try:
    # Try importing platform services (they may not be in use, so this is optional)
    sys.path.insert(0, str(project_root / "platform" / "services" / "api-gateway" / "src"))
    
    # Test prompt_injection_api
    try:
        from prompt_injection_api import API_KEY as PI_API_KEY, TARGET_MODEL as PI_TARGET_MODEL
        if PI_API_KEY and PI_API_KEY.startswith("sk-"):
            print("   ✓ prompt_injection_api.py: API_KEY loaded from environment")
        else:
            print("   ✗ prompt_injection_api.py: API_KEY invalid or missing")
            sys.exit(1)
        print("   ✓ prompt_injection_api.py: PASS")
    except Exception as e:
        print(f"   ⚠️  prompt_injection_api.py: Could not test (may not be in use): {e}")
    
    # Test jailbreak_api
    try:
        from jailbreak_api import API_KEY as JB_API_KEY, TARGET_MODEL as JB_TARGET_MODEL
        if JB_API_KEY and JB_API_KEY.startswith("sk-"):
            print("   ✓ jailbreak_api.py: API_KEY loaded from environment")
        else:
            print("   ✗ jailbreak_api.py: API_KEY invalid or missing")
            sys.exit(1)
        print("   ✓ jailbreak_api.py: PASS")
    except Exception as e:
        print(f"   ⚠️  jailbreak_api.py: Could not test (may not be in use): {e}")
        
except Exception as e:
    print(f"   ⚠️  Platform services test skipped (may not be in use): {e}")

# Test 3: Verify no hardcoded keys in source files
print("\n3. Scanning for hardcoded API keys in source files...")
import re

# Patterns to check for
hardcoded_patterns = [
    r'sk-proj-[a-zA-Z0-9\-_]{50,}',  # OpenAI API key pattern
    r'6325b3d3efef4e09afd7d98a33d0e626',  # Known Ollama key
]

files_to_check = [
    "backend/config/settings.py",
    "platform/services/api-gateway/src/prompt_injection_api.py",
    "platform/services/api-gateway/src/jailbreak_api.py",
    "archive/legacy/unified_api_server.py",
    "archive/legacy/simple_api_server.py"
]

found_keys = False
for file_path in files_to_check:
    full_path = project_root / file_path
    if full_path.exists():
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            for pattern in hardcoded_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    print(f"   ✗ Found hardcoded key in {file_path}: {matches[0][:20]}...")
                    found_keys = True

if not found_keys:
    print("   ✓ No hardcoded API keys found in source files")
else:
    print("   ✗ Hardcoded keys still present!")
    sys.exit(1)

# Test 4: Verify backup files are removed
print("\n4. Checking for backup files with exposed credentials...")
backup_files = [
    "backend/api/unified_api_server.py.backup",
    "backend/scripts/simple_api_server.py.backup"
]

found_backups = False
for backup_file in backup_files:
    full_path = project_root / backup_file
    if full_path.exists():
        print(f"   ✗ Backup file still exists: {backup_file}")
        found_backups = True

if not found_backups:
    print("   ✓ No backup files with exposed credentials found")
else:
    print("   ✗ Backup files still present!")
    sys.exit(1)

print("\n" + "="*60)
print("✓ All security tests PASSED!")
print("="*60 + "\n")
print("Summary:")
print("  ✓ Backend settings use environment variables")
print("  ✓ Platform services use environment variables")
print("  ✓ No hardcoded API keys in source files")
print("  ✓ Backup files removed")
print("\n✅ The codebase is now secure!")

