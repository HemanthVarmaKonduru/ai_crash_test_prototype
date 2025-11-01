"""
Application configuration settings.
"""
import os
from pathlib import Path

# Base directory (parent of backend)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# API Configuration
API_KEY = os.getenv("OPENAI_API_KEY", "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")
TARGET_MODEL = "gpt-3.5-turbo"  # Model to test (overrides user input)
JUDGE_MODEL = "gpt-4o-mini"     # Model for evaluation

# Test limits
MAX_PROMPTS_PI = 30  # Limit to first 30 prompts for prompt injection
MAX_PROMPTS_JB = 15  # Limit to first 15 prompts for jailbreak
MAX_PROMPTS_DE = 20  # Limit to first 20 prompts for data extraction

# Authentication configuration
VALID_EMAIL = "testuser@123"
VALID_PASSWORD = "Cars@$98"
SESSION_EXPIRY_HOURS = 24

# Data paths (relative to project root)
DATA_DIR = BASE_DIR / "data"
PROMPT_INJECTION_DATASET = DATA_DIR / "prompt_injection_comprehensive_processed.json"
JAILBREAK_DATASET = DATA_DIR / "jailbreak.json"
DATA_EXTRACTION_DATASET = DATA_DIR / "data_extraction_comprehensive.json"

# CORS settings - supports environment variable for production
CORS_ORIGINS_ENV = os.getenv("CORS_ORIGINS", "")
CORS_ORIGINS = (
    CORS_ORIGINS_ENV.split(",") if CORS_ORIGINS_ENV
    else ["http://localhost:3000", "http://localhost:3001"]
)

