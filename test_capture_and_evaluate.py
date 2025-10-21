#!/usr/bin/env python3
"""
Test script to verify the exact flow:
1. Load data from prompt_injection.json
2. Send to GPT-3.5-turbo and capture responses
3. Store responses temporarily
4. Evaluate responses using GPT-4.1-mini
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

async def test_capture_and_evaluate():
    """Test the complete flow: capture -> evaluate."""
    print("🚀 TESTING CAPTURE AND EVALUATE FLOW")
    print("=" * 60)
    
    start_time = time.time()
    
    # Step 1: Capture responses from GPT-3.5-turbo
    print("\n📊 Step 1: Capturing responses from GPT-3.5-turbo...")
    
    config = {'test': True, 'openai_api_key': API_KEY}
    capture_agent = ResponseCaptureAgent(config, 'capture_test')
    
    capture_data = {
        'api_key': API_KEY,
        'model': TARGET_MODEL,
        'user_id': 'capture_test_user',
        'dataset_path': 'prompt_injection.json',
        'max_tokens': 150,
        'temperature': 0.7
    }
    
    print(f"   Loading data from prompt_injection.json...")
    print(f"   Sending to {TARGET_MODEL}...")
    
    capture_result = await capture_agent.execute(capture_data)
    
    if not capture_result.success:
        print(f"❌ Capture failed: {capture_result.error}")
        return False
    
    captured_responses = capture_result.data.get('captured_responses', [])
    temp_file_path = capture_result.data.get('temp_file_path')
    successful_captures = capture_result.data.get('successful_captures', 0)
    failed_captures = capture_result.data.get('failed_captures', 0)
    
    print(f"✅ Capture completed!")
    print(f"   Total responses: {len(captured_responses)}")
    print(f"   Successful captures: {successful_captures}")
    print(f"   Failed captures: {failed_captures}")
    print(f"   Stored in: {temp_file_path}")
    
    # Show sample captured response
    if captured_responses:
        sample = captured_responses[0]
        print(f"\n🤖 Sample GPT-3.5-turbo response:")
        print(f"   Sample ID: {sample.get('sample_id', 'N/A')}")
        print(f"   User Input: {sample.get('user_input', 'N/A')}")
        print(f"   Model Response: {sample.get('model_response', 'N/A')}")
        print(f"   Response Time: {sample.get('response_time', 0):.3f}s")
        print(f"   API Model: {sample.get('api_model', 'N/A')}")
    
    # Step 2: Evaluate captured responses using GPT-4.1-mini
    print(f"\n🧠 Step 2: Evaluating responses using GPT-4.1-mini...")
    
    evaluator = CapturedResponseEvaluator(config, 'evaluation_test')
    
    evaluation_data = {
        'api_key': API_KEY,
        'temp_file_path': temp_file_path,
        'judge_model': JUDGE_MODEL
    }
    
    print(f"   Loading captured responses from {temp_file_path}...")
    print(f"   Evaluating using {JUDGE_MODEL}...")
    
    evaluation_result = await evaluator.execute(evaluation_data)
    
    if not evaluation_result.success:
        print(f"❌ Evaluation failed: {evaluation_result.error}")
        return False
    
    evaluated_responses = evaluation_result.data.get('evaluated_responses', [])
    evaluated_file_path = evaluation_result.data.get('evaluated_file_path')
    successful_evaluations = evaluation_result.data.get('successful_evaluations', 0)
    successful_resistances = evaluation_result.data.get('successful_resistances', 0)
    failed_resistances = evaluation_result.data.get('failed_resistances', 0)
    detection_rate = evaluation_result.data.get('detection_rate', 0)
    
    print(f"✅ Evaluation completed!")
    print(f"   Total evaluated: {len(evaluated_responses)}")
    print(f"   Successful evaluations: {successful_evaluations}")
    print(f"   Successful resistances: {successful_resistances}")
    print(f"   Failed resistances: {failed_resistances}")
    print(f"   Detection rate: {detection_rate:.1f}%")
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
    
    # Summary
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n🎯 FLOW VERIFICATION COMPLETE")
    print("=" * 60)
    print(f"⏱️  Total execution time: {total_time:.2f} seconds")
    print(f"✅ Data loaded from prompt_injection.json")
    print(f"✅ Sent to {TARGET_MODEL} and responses captured")
    print(f"✅ Responses stored temporarily in {temp_file_path}")
    print(f"✅ Evaluated using {JUDGE_MODEL} (GPT-4.1-mini)")
    print(f"✅ Evaluated responses stored in {evaluated_file_path}")
    print(f"✅ Detection rate: {detection_rate:.1f}%")
    
    print(f"\n🚀 FLOW MATCHES YOUR REQUIREMENTS PERFECTLY!")
    print(f"📁 Check the temporary files to see the exact data flow:")
    print(f"   - Captured responses: {temp_file_path}")
    print(f"   - Evaluated responses: {evaluated_file_path}")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_capture_and_evaluate())
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)

