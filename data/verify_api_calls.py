#!/usr/bin/env python3
"""
Verify OpenAI API Calls

This script makes a simple test call to verify the API key is working
and shows usage information.
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/hv/Desktop/Hemanth/AI/AI_Projects_Karun/ai_crash_test_prototype/.env')

def test_openai_api():
    """Test OpenAI API with a simple call."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables!")
        return
    
    print(f"🔑 Using API Key: {api_key[:20]}...")
    
    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Hello! Please respond with exactly: 'API_TEST_SUCCESS' and nothing else."}
        ],
        "max_tokens": 10,
        "temperature": 0
    }
    
    try:
        print("🚀 Making test API call to OpenAI...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")
            print(f"📝 Response: {result['choices'][0]['message']['content']}")
            
            # Show usage information
            if 'usage' in result:
                usage = result['usage']
                print(f"📈 Usage:")
                print(f"   - Prompt tokens: {usage.get('prompt_tokens', 0)}")
                print(f"   - Completion tokens: {usage.get('completion_tokens', 0)}")
                print(f"   - Total tokens: {usage.get('total_tokens', 0)}")
            
            # Show model information
            print(f"🤖 Model: {result.get('model', 'Unknown')}")
            print(f"🆔 Request ID: {result.get('id', 'Unknown')}")
            
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error making API call: {str(e)}")

def check_usage():
    """Check usage information from OpenAI API."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found!")
        return
    
    print("\n📊 Checking usage information...")
    
    # Try to get usage information (this might not work with all API keys)
    try:
        url = "https://api.openai.com/v1/usage"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Usage API Status: {response.status_code}")
        
        if response.status_code == 200:
            usage_data = response.json()
            print("📈 Usage Data:")
            print(json.dumps(usage_data, indent=2))
        else:
            print(f"Usage API not accessible: {response.text}")
            
    except Exception as e:
        print(f"Usage API error: {str(e)}")

if __name__ == "__main__":
    print("🔍 OpenAI API Verification Test")
    print("="*50)
    
    test_openai_api()
    check_usage()
    
    print("\n" + "="*50)
    print("✅ Verification complete!")
    print("💡 If you see 'API_TEST_SUCCESS' above, the API calls are working!")
    print("💡 Check your OpenAI dashboard for usage logs (may take a few minutes to appear)")

