#!/usr/bin/env python3
"""
Test Prompt Injection using existing API Gateway

This script tests prompt injection using your existing API Gateway service
with the comprehensive dataset we created.
"""

import requests
import json
import time

def test_prompt_injection(api_key: str, num_samples: int = 10):
    """Test prompt injection using the API Gateway."""
    
    # API Gateway URL
    base_url = "http://localhost:8000"
    
    print("🎯 Testing Prompt Injection with API Gateway")
    print("="*50)
    
    # Test data
    test_request = {
        "num_samples": num_samples,
        "model": "gpt-3.5-turbo",
        "api_key": api_key
    }
    
    try:
        # Start the test
        print(f"🚀 Starting test with {num_samples} samples...")
        response = requests.post(
            f"{base_url}/test/prompt-injection",
            json=test_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            test_id = result.get("test_id")
            print(f"✅ Test started successfully!")
            print(f"📊 Test ID: {test_id}")
            print(f"📈 Samples: {result.get('num_samples')}")
            
            # Wait a bit for the test to run
            print(f"\n⏳ Waiting for test to complete...")
            time.sleep(5)
            
            # Get results
            results_response = requests.get(f"{base_url}/test/prompt-injection/{test_id}")
            if results_response.status_code == 200:
                results = results_response.json()
                print(f"📋 Results: {results}")
            else:
                print(f"❌ Failed to get results: {results_response.status_code}")
                
        else:
            print(f"❌ Failed to start test: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API Gateway. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Main function."""
    print("🎯 Prompt Injection Testing with API Gateway")
    print("="*50)
    
    # Get API key
    api_key = input("Enter your OpenAI API key: ").strip()
    if not api_key:
        print("❌ API key is required!")
        return
    
    # Get number of samples
    try:
        num_samples = int(input("Enter number of samples to test (default 10): ") or "10")
    except ValueError:
        num_samples = 10
    
    # Run the test
    test_prompt_injection(api_key, num_samples)

if __name__ == "__main__":
    main()

