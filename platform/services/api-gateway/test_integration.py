"""
Integration test script for API Gateway.

Tests the backend API endpoints to ensure they're working correctly.
"""

import requests
import json
import time

# API Gateway URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint."""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API Gateway. Is it running?")
        return False

def test_model_connection():
    """Test model connection endpoint."""
    print("\n🔍 Testing model connection...")
    
    # Test data
    test_data = {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "api_key": "sk-test123456789",  # This will fail connection test
        "name": "Test GPT-3.5 Model",
        "config": {
            "temperature": 0.7,
            "max_tokens": 1000
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/models/connect", json=test_data)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Model connection response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Model connection failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Model connection error: {e}")
        return False

def test_list_models():
    """Test list models endpoint."""
    print("\n🔍 Testing list models...")
    
    try:
        response = requests.get(f"{BASE_URL}/models")
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ List models response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ List models failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ List models error: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🚀 Starting API Gateway Integration Tests")
    print("=" * 50)
    
    # Test health check first
    if not test_health_check():
        print("\n❌ Backend not running. Please start the API Gateway first:")
        print("   cd platform/services/api-gateway")
        print("   python src/main.py")
        return
    
    # Test model connection
    test_model_connection()
    
    # Test list models
    test_list_models()
    
    print("\n" + "=" * 50)
    print("✅ Integration tests completed!")

if __name__ == "__main__":
    main()

