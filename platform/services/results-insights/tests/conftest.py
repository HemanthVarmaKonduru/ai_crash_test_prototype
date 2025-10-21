"""
Pytest configuration and fixtures for results-insights tests.
"""

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from main import app

@pytest.fixture
def api_client():
    """Create test client for Results & Insights API."""
    return TestClient(app)

@pytest.fixture
def sample_model_id():
    """Sample model ID for testing."""
    return "demo-user-123:openai:gpt-3.5-turbo"

@pytest.fixture
def sample_user_id():
    """Sample user ID for testing."""
    return "demo-user-123"

@pytest.fixture
def sample_test_results():
    """Sample test results for testing."""
    return {
        "model_id": "demo-user-123:openai:gpt-3.5-turbo",
        "user_id": "demo-user-123",
        "test_suite": "safety",
        "overall_score": 85.5,
        "total_tests": 10,
        "passed_tests": 8,
        "failed_tests": 2,
        "severity_breakdown": {
            "low": 1,
            "medium": 1,
            "high": 0,
            "critical": 0
        },
        "timestamp": "2025-01-18T10:00:00Z",
        "test_details": [
            {
                "test_name": "Test 1",
                "status": "passed",
                "score": 90.0,
                "severity": "low",
                "details": "Test 1 details"
            },
            {
                "test_name": "Test 2",
                "status": "failed",
                "score": 60.0,
                "severity": "medium",
                "details": "Test 2 details"
            }
        ]
    }

