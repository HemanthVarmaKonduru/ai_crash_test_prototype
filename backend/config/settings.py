"""
Application configuration settings.
"""
import os
from pathlib import Path

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    # Base directory (parent of backend)
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded .env from {env_path}")
    else:
        print(f"⚠️ .env file not found at {env_path}, using environment variables only")
except ImportError:
    print("⚠️ python-dotenv not installed, using environment variables only")
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

# API Configuration
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required. Please set it in your .env file.")

TARGET_MODEL = os.getenv("TARGET_MODEL", "gpt-3.5-turbo")  # Model to test (overrides user input)
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "gpt-4o-mini")     # Model for evaluation

# Ollama Cloud Configuration
USE_OLLAMA_FOR_EVALUATION = os.getenv("USE_OLLAMA_FOR_EVALUATION", "true").lower() == "true"
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "https://ollama.com")
OLLAMA_JUDGE_MODEL = os.getenv("OLLAMA_JUDGE_MODEL", "glm-4.6:cloud")  # Ollama model for evaluation
OLLAMA_FIREWALL_MODEL = os.getenv("OLLAMA_FIREWALL_MODEL", "gpt-oss:20b-cloud")  # Ollama model for firewall chat

# Validate Ollama configuration if using Ollama for evaluation
if USE_OLLAMA_FOR_EVALUATION and not OLLAMA_API_KEY:
    raise ValueError("OLLAMA_API_KEY environment variable is required when USE_OLLAMA_FOR_EVALUATION is true. Please set it in your .env file.")

# Test limits
MAX_PROMPTS_PI = 30  # Limit to first 30 prompts for prompt injection
MAX_PROMPTS_JB = 15  # Limit to first 15 prompts for jailbreak
MAX_PROMPTS_DE = 20  # Limit to first 20 prompts for data extraction
MAX_PROMPTS_ADVERSARIAL = 30  # Limit to first 30 prompts for adversarial attacks

# Authentication configuration
VALID_EMAIL = os.getenv("VALID_EMAIL")
VALID_PASSWORD = os.getenv("VALID_PASSWORD")
SESSION_EXPIRY_HOURS = int(os.getenv("SESSION_EXPIRY_HOURS", "24"))

# Validate authentication credentials
if not VALID_EMAIL or not VALID_PASSWORD:
    raise ValueError("VALID_EMAIL and VALID_PASSWORD environment variables are required. Please set them in your .env file.")

# Data paths (relative to project root)
DATA_DIR = BASE_DIR / "data"
PROMPT_INJECTION_DATASET = DATA_DIR / "prompt_injection_comprehensive_processed.json"
JAILBREAK_DATASET = DATA_DIR / "jailbreak.json"
DATA_EXTRACTION_DATASET = DATA_DIR / "data_extraction_comprehensive.json"
ADVERSARIAL_ATTACKS_DATASET = DATA_DIR / "modules" / "adversarial_attacks" / "adversarial_attacks_test_30.json"

# CORS settings - supports environment variable for production
CORS_ORIGINS_ENV = os.getenv("CORS_ORIGINS", "")
CORS_ORIGINS = (
    CORS_ORIGINS_ENV.split(",") if CORS_ORIGINS_ENV
    else ["http://localhost:3000", "http://localhost:3001","https://ai-crash-test-prototype.vercel.app"]
)

