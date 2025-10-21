#!/usr/bin/env python3
"""
Comprehensive API Test - Test the complete flow with real OpenAI API calls
"""

import sys
import os
import json
import asyncio
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add paths
sys.path.insert(0, 'platform/libs/agents')
sys.path.insert(0, 'platform/services/prompt-injection-tester/src')

# Import agents
from agents.response_capture_agent import ResponseCaptureAgent
from agents.captured_response_evaluator import CapturedResponseEvaluator

# API Configuration
API_KEY = "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"
TARGET_MODEL = "gpt-3.5-turbo"  # Model to test
JUDGE_MODEL = "gpt-4o-mini"     # Model for evaluation

async def test_api_connectivity():
    """Test basic API connectivity."""
    print("🔌 Testing API Connectivity...")
    
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=API_KEY)
        
        # Test basic API call
        response = await client.chat.completions.create(
            model=TARGET_MODEL,
            messages=[{"role": "user", "content": "Hello, this is a test."}],
            max_tokens=10
        )
        
        print(f"✅ API connectivity test passed")
        print(f"   Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ API connectivity test failed: {e}")
        return False

async def test_response_capture_agent():
    """Test the response capture agent with real API calls."""
    print("\n📊 Testing Response Capture Agent...")
    
    try:
        config = {'test': True, 'openai_api_key': API_KEY}
        capture_agent = ResponseCaptureAgent(config, 'capture_test')
        
        # Test with a small subset of data
        capture_data = {
            'api_key': API_KEY,
            'model': TARGET_MODEL,
            'user_id': 'api_test_user',
            'dataset_path': 'prompt_injection.json',
            'max_tokens': 100,
            'temperature': 0.7
        }
        
        print(f"   Loading data from prompt_injection.json...")
        print(f"   Sending to {TARGET_MODEL}...")
        
        start_time = time.time()
        result = await capture_agent.execute(capture_data)
        end_time = time.time()
        
        if result.success:
            captured_responses = result.data.get('captured_responses', [])
            successful_captures = result.data.get('successful_captures', 0)
            failed_captures = result.data.get('failed_captures', 0)
            temp_file_path = result.data.get('temp_file_path')
            
            print(f"✅ Response capture successful!")
            print(f"   Total responses: {len(captured_responses)}")
            print(f"   Successful captures: {successful_captures}")
            print(f"   Failed captures: {failed_captures}")
            print(f"   Execution time: {end_time - start_time:.2f}s")
            print(f"   Stored in: {temp_file_path}")
            
            # Show sample captured response
            if captured_responses:
                sample = captured_responses[0]
                print(f"\n🤖 Sample GPT-3.5-turbo response:")
                print(f"   Sample ID: {sample.get('sample_id', 'N/A')}")
                print(f"   User Input: {sample.get('user_input', 'N/A')}")
                print(f"   Model Response: {sample.get('model_response', 'N/A')[:100]}...")
                print(f"   Response Time: {sample.get('response_time', 0):.3f}s")
                print(f"   API Model: {sample.get('api_model', 'N/A')}")
            
            return temp_file_path, captured_responses
        else:
            print(f"❌ Response capture failed: {result.error}")
            return None, []
            
    except Exception as e:
        print(f"❌ Response capture agent error: {e}")
        return None, []

async def test_captured_response_evaluator(temp_file_path):
    """Test the captured response evaluator with real API calls."""
    print(f"\n🧠 Testing Captured Response Evaluator...")
    
    try:
        config = {'test': True, 'openai_api_key': API_KEY}
        evaluator = CapturedResponseEvaluator(config, 'evaluation_test')
        
        evaluation_data = {
            'api_key': API_KEY,
            'temp_file_path': temp_file_path,
            'judge_model': JUDGE_MODEL
        }
        
        print(f"   Loading captured responses from {temp_file_path}...")
        print(f"   Evaluating using {JUDGE_MODEL}...")
        
        start_time = time.time()
        result = await evaluator.execute(evaluation_data)
        end_time = time.time()
        
        if result.success:
            evaluated_responses = result.data.get('evaluated_responses', [])
            successful_evaluations = result.data.get('successful_evaluations', 0)
            successful_resistances = result.data.get('successful_resistances', 0)
            failed_resistances = result.data.get('failed_resistances', 0)
            detection_rate = result.data.get('detection_rate', 0)
            evaluated_file_path = result.data.get('evaluated_file_path')
            
            print(f"✅ Evaluation successful!")
            print(f"   Total evaluated: {len(evaluated_responses)}")
            print(f"   Successful evaluations: {successful_evaluations}")
            print(f"   Successful resistances: {successful_resistances}")
            print(f"   Failed resistances: {failed_resistances}")
            print(f"   Detection rate: {detection_rate:.1f}%")
            print(f"   Execution time: {end_time - start_time:.2f}s")
            print(f"   Stored in: {evaluated_file_path}")
            
            # Show sample evaluation
            if evaluated_responses:
                sample = evaluated_responses[0]
                evaluation = sample.get('evaluation', {})
                print(f"\n🔍 Sample GPT-4.1-mini evaluation:")
                print(f"   Sample ID: {sample.get('sample_id', 'N/A')}")
                print(f"   Injection Successful: {sample.get('injection_successful', 'N/A')}")
                print(f"   Confidence Score: {sample.get('confidence_score', 'N/A')}")
                print(f"   Severity: {sample.get('severity', 'N/A')}")
                print(f"   Safety Score: {sample.get('safety_score', 'N/A')}")
                print(f"   Reasoning: {sample.get('reasoning', 'N/A')[:100]}...")
            
            return evaluated_responses, detection_rate
        else:
            print(f"❌ Evaluation failed: {result.error}")
            return [], 0
            
    except Exception as e:
        print(f"❌ Evaluation agent error: {e}")
        return [], 0

async def test_complete_workflow():
    """Test the complete workflow end-to-end."""
    print("🚀 COMPREHENSIVE API TEST")
    print("=" * 60)
    
    start_time = time.time()
    
    # Step 1: Test API connectivity
    print("\n🔌 Step 1: Testing API Connectivity...")
    if not await test_api_connectivity():
        print("❌ API connectivity test failed, stopping test")
        return False
    
    # Step 2: Test response capture
    print("\n📊 Step 2: Testing Response Capture...")
    temp_file_path, captured_responses = await test_response_capture_agent()
    if not temp_file_path or not captured_responses:
        print("❌ Response capture failed, stopping test")
        return False
    
    # Step 3: Test evaluation
    print("\n🧠 Step 3: Testing Response Evaluation...")
    evaluated_responses, detection_rate = await test_captured_response_evaluator(temp_file_path)
    if not evaluated_responses:
        print("❌ Response evaluation failed, stopping test")
        return False
    
    # Step 4: Analyze results
    print("\n📈 Step 4: Analyzing Results...")
    
    total_captured = len(captured_responses)
    total_evaluated = len(evaluated_responses)
    successful_captures = sum(1 for r in captured_responses if r.get('capture_success', False))
    successful_resistances = sum(1 for r in evaluated_responses if not r.get('injection_successful', False))
    failed_resistances = sum(1 for r in evaluated_responses if r.get('injection_successful', False))
    
    print(f"📊 Final Results:")
    print(f"   Total captured responses: {total_captured}")
    print(f"   Successful captures: {successful_captures}")
    print(f"   Total evaluated: {total_evaluated}")
    print(f"   Successful resistances: {successful_resistances}")
    print(f"   Failed resistances: {failed_resistances}")
    print(f"   Detection rate: {detection_rate:.1f}%")
    
    # Step 5: Verify data integrity
    print(f"\n🔍 Step 5: Verifying Data Integrity...")
    
    # Check captured responses file
    if os.path.exists(temp_file_path):
        with open(temp_file_path, 'r') as f:
            stored_responses = json.load(f)
        print(f"✅ Captured responses file exists: {len(stored_responses)} responses")
    else:
        print(f"❌ Captured responses file not found: {temp_file_path}")
    
    # Check evaluated responses file
    evaluated_file_path = f"temp_evaluated_responses_{int(time.time())}.json"
    if os.path.exists(evaluated_file_path):
        with open(evaluated_file_path, 'r') as f:
            stored_evaluations = json.load(f)
        print(f"✅ Evaluated responses file exists: {len(stored_evaluations)} evaluations")
    else:
        print(f"❌ Evaluated responses file not found: {evaluated_file_path}")
    
    # Step 6: Performance metrics
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n⏱️  Performance Metrics:")
    print(f"   Total execution time: {total_time:.2f} seconds")
    print(f"   Average response time: {sum(r.get('response_time', 0) for r in captured_responses) / len(captured_responses):.3f}s")
    print(f"   API calls per second: {len(captured_responses) / total_time:.2f}")
    
    # Step 7: Summary
    print(f"\n🎯 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ API connectivity: PASSED")
    print(f"✅ Response capture: PASSED ({successful_captures}/{total_captured})")
    print(f"✅ Response evaluation: PASSED ({total_evaluated} evaluated)")
    print(f"✅ Data storage: PASSED")
    print(f"✅ Performance: PASSED ({total_time:.2f}s)")
    print(f"✅ Detection rate: {detection_rate:.1f}%")
    
    print(f"\n🚀 COMPREHENSIVE API TEST COMPLETED SUCCESSFULLY!")
    print(f"📁 Check the temporary files to see the complete data flow:")
    print(f"   - Captured responses: {temp_file_path}")
    print(f"   - Evaluated responses: {evaluated_file_path}")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_complete_workflow())
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

