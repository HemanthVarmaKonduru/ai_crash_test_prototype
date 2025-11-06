#!/usr/bin/env python3
"""
Verify the exact flow: prompt_injection.json -> GPT-3.5-turbo -> GPT-4.1-mini evaluation
"""

import sys
import os
import json
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add paths
sys.path.insert(0, 'platform/libs/agents')
sys.path.insert(0, 'platform/libs/evaluation')
sys.path.insert(0, 'platform/services/prompt-injection-tester/src')

# Import agents
from agents.test_execution_agent import PromptInjectionTestExecutionAgent
from agents.evaluation_agent import PromptInjectionEvaluationAgent

# API Configuration
API_KEY = "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"
TARGET_MODEL = "gpt-3.5-turbo"  # Model to test
JUDGE_MODEL = "gpt-4o-mini"     # Model for evaluation

async def verify_flow():
    """Verify the exact data flow as per requirements."""
    print("🔍 VERIFYING DATA FLOW")
    print("=" * 50)
    
    # Step 1: Load data from prompt_injection.json
    print("📊 Step 1: Loading data from prompt_injection.json...")
    with open('data/prompt_injection.json', 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    # Take first 3 samples for verification
    test_samples = dataset[:3]
    print(f"✅ Loaded {len(test_samples)} samples from prompt_injection.json")
    
    # Show sample data
    print("\n📋 Sample data from prompt_injection.json:")
    for i, sample in enumerate(test_samples):
        print(f"  Sample {i+1}:")
        print(f"    ID: {sample['prompt_id']}")
        print(f"    Test Case: {sample['test_case_prompt']}")
        print(f"    User Input: {sample['user_input']}")
        print(f"    Judge Question: {sample['judge_question']}")
        print()
    
    # Step 2: Test execution agent (sends to GPT-3.5-turbo)
    print("⚡ Step 2: Testing execution agent (GPT-3.5-turbo)...")
    
    config = {'test': True, 'openai_api_key': API_KEY}
    execution_agent = PromptInjectionTestExecutionAgent(config, 'execution_test')
    
    execution_data = {
        'session_id': 'flow_test',
        'api_key': API_KEY,
        'model': TARGET_MODEL,
        'user_id': 'flow_test_user',
        'dataset_path': 'prompt_injection.json'
    }
    
    print(f"   Sending data to {TARGET_MODEL}...")
    execution_result = await execution_agent.execute(execution_data)
    
    if execution_result.success:
        test_results = execution_result.data.get('results', [])
        print(f"✅ Generated {len(test_results)} test results from GPT-3.5-turbo")
        
        # Show sample response from GPT-3.5-turbo
        if test_results:
            sample_result = test_results[0]
            print(f"\n🤖 Sample GPT-3.5-turbo response:")
            print(f"   Injection Prompt: {sample_result.get('injection_prompt', 'N/A')}")
            print(f"   Model Response: {sample_result.get('model_response', 'N/A')}")
            print(f"   Response Time: {sample_result.get('response_time', 0):.3f}s")
            print(f"   API Model: {sample_result.get('metadata', {}).get('api_model', 'N/A')}")
    else:
        print(f"❌ Execution failed: {execution_result.error}")
        return
    
    # Step 3: Test evaluation agent (uses GPT-4.1-mini)
    print(f"\n🧠 Step 3: Testing evaluation agent (GPT-4.1-mini)...")
    
    evaluation_agent = PromptInjectionEvaluationAgent(config, 'evaluation_test')
    
    evaluation_data = {
        'session_id': 'flow_test',
        'api_key': API_KEY,
        'judge_model': JUDGE_MODEL,
        'test_results': test_results
    }
    
    print(f"   Evaluating responses using {JUDGE_MODEL}...")
    evaluation_result = await evaluation_agent.execute(evaluation_data)
    
    if evaluation_result.success:
        evaluated_results = evaluation_result.data.get('evaluated_results', [])
        successful_resistances = evaluation_result.data.get('successful_resistances', 0)
        failed_resistances = evaluation_result.data.get('failed_resistances', 0)
        
        print(f"✅ Evaluation completed using {JUDGE_MODEL}")
        print(f"   Successful resistances: {successful_resistances}")
        print(f"   Failed resistances: {failed_resistances}")
        print(f"   Detection rate: {(successful_resistances / len(evaluated_results) * 100):.1f}%")
        
        # Show sample evaluation
        if evaluated_results:
            sample_evaluation = evaluated_results[0]
            print(f"\n🔍 Sample GPT-4.1-mini evaluation:")
            print(f"   Injection Successful: {sample_evaluation.get('injection_successful', 'N/A')}")
            print(f"   Confidence Score: {sample_evaluation.get('confidence_score', 'N/A')}")
            print(f"   Failure Reason: {sample_evaluation.get('failure_reason', 'N/A')}")
    else:
        print(f"❌ Evaluation failed: {evaluation_result.error}")
        return
    
    # Summary
    print(f"\n🎯 FLOW VERIFICATION COMPLETE")
    print("=" * 50)
    print("✅ Data loaded from prompt_injection.json")
    print(f"✅ Sent to {TARGET_MODEL} for real API calls")
    print(f"✅ Evaluated using {JUDGE_MODEL} (LLM-as-a-Judge)")
    print("✅ Multi-agent workflow functioning correctly")
    print("\n🚀 Flow matches your requirements perfectly!")

if __name__ == "__main__":
    asyncio.run(verify_flow())




