"""
End-to-End Test with Real GPT-3.5-turbo API Calls

This test script:
1. Makes REAL API calls to GPT-3.5-turbo to get actual model responses
2. Uses the new multi-layer evaluation system to evaluate those real responses
3. Provides detailed reporting and statistics

IMPORTANT: This test makes actual API calls and will consume OpenAI credits.
"""
import pytest
import json
import sys
import os
import asyncio
import time
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded .env from {env_path}")
    else:
        print(f"⚠ .env file not found at {env_path}, using environment variables")
except ImportError:
    print("⚠ python-dotenv not installed, using environment variables only")

from openai import AsyncOpenAI

from backend.config.settings import (
    API_KEY,
    TARGET_MODEL,
    PROMPT_INJECTION_DATASET,
    MAX_PROMPTS_PI
)
from backend.services.prompt_injection.evaluation import (
    PromptInjectionEvaluator,
    EvaluationContext,
    create_evaluator_with_defaults
)
from backend.services.prompt_injection.evaluation.types import (
    EvaluationOutcome,
    EvaluationLayer
)


@pytest.fixture
def test_dataset():
    """Load test dataset."""
    dataset_path = PROMPT_INJECTION_DATASET
    
    # Fallback to limited dataset if comprehensive not found
    if not dataset_path.exists():
        dataset_path = project_root / "data" / "prompt_injection_limited_30.json"
    
    if not dataset_path.exists():
        pytest.skip(f"Dataset not found at {dataset_path}")
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Handle different dataset formats
        if 'prompt_injection_samples' in data:
            return data['prompt_injection_samples'][:MAX_PROMPTS_PI]
        elif isinstance(data, list):
            return data[:MAX_PROMPTS_PI]
        else:
            return []


@pytest.fixture
async def openai_client():
    """Create OpenAI client with API key from environment."""
    api_key = API_KEY
    if not api_key or api_key.startswith("sk-proj-") and len(api_key) < 50:
        pytest.skip("OpenAI API key not properly configured in .env or settings.py")
    
    client = AsyncOpenAI(api_key=api_key)
    return client


@pytest.fixture
async def evaluator():
    """Create and initialize evaluator."""
    eval_instance = create_evaluator_with_defaults()
    await eval_instance.initialize()
    return eval_instance


@pytest.mark.asyncio
@pytest.mark.slow
async def test_real_api_calls_and_evaluation(openai_client, evaluator, test_dataset):
    """
    End-to-end test with real GPT-3.5-turbo API calls.
    
    This test:
    1. Makes real API calls to GPT-3.5-turbo for each test sample
    2. Captures actual model responses
    3. Evaluates responses using the new multi-layer evaluation system
    4. Provides detailed statistics and reporting
    """
    print("\n" + "="*80)
    print("🚀 Starting End-to-End Test with Real GPT-3.5-turbo API Calls")
    print("="*80)
    print(f"Target Model: {TARGET_MODEL}")
    print(f"Number of samples: {len(test_dataset)}")
    print(f"Evaluation System: Multi-Layer Evaluation")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*80 + "\n")
    
    if not test_dataset:
        pytest.skip("No test samples found in dataset")
    
    # Limit to first 5 samples for initial testing (to save API costs)
    # Change this to len(test_dataset) for full test
    test_samples = test_dataset[:5]
    
    results = []
    api_call_times = []
    evaluation_times = []
    total_start = time.time()
    
    for i, sample in enumerate(test_samples, 1):
        print(f"\n[{i}/{len(test_samples)}] Processing sample: {sample.get('sample_id', f'sample_{i}')}")
        print(f"  Category: {sample.get('category', 'unknown')}")
        print(f"  Technique: {sample.get('technique', 'unknown')}")
        print(f"  Injection Prompt: {sample.get('injection_prompt', '')[:100]}...")
        
        # Step 1: Make real API call to GPT-3.5-turbo
        api_start = time.time()
        try:
            response = await openai_client.chat.completions.create(
                model=TARGET_MODEL,
                messages=[
                    {"role": "system", "content": sample.get('base_prompt', 'You are a helpful AI assistant.')},
                    {"role": "user", "content": sample.get('injection_prompt', '')}
                ],
                max_tokens=150,
                temperature=0.7
            )
            api_time = time.time() - api_start
            api_call_times.append(api_time)
            
            model_response = response.choices[0].message.content
            print(f"  ✓ API call completed in {api_time:.2f}s")
            print(f"  Response: {model_response[:150]}...")
            
        except Exception as e:
            print(f"  ✗ API call failed: {e}")
            results.append({
                'sample_id': sample.get('sample_id', f'sample_{i}'),
                'error': str(e),
                'api_call_success': False
            })
            continue
        
        # Step 2: Evaluate using new multi-layer evaluation system
        eval_start = time.time()
        try:
            context = EvaluationContext(
                injection_prompt=sample.get('injection_prompt', ''),
                model_response=model_response,
                base_prompt=sample.get('base_prompt', ''),
                sample_metadata={
                    'sample_id': sample.get('sample_id', ''),
                    'category': sample.get('category', 'unknown'),
                    'technique': sample.get('technique', 'unknown'),
                    'severity': sample.get('severity', 'unknown'),
                    'language': sample.get('language', 'English')
                },
                response_time=api_time
            )
            
            evaluation_result = await evaluator.evaluate(context)
            eval_time = time.time() - eval_start
            evaluation_times.append(eval_time)
            
            print(f"  ✓ Evaluation completed in {eval_time:.2f}s")
            print(f"  Outcome: {evaluation_result.outcome.value}")
            print(f"  Injection Successful: {evaluation_result.injection_successful}")
            print(f"  Confidence: {evaluation_result.confidence_score:.2f}")
            print(f"  Safety Score: {evaluation_result.safety_score:.2f}")
            print(f"  Layer Used: {evaluation_result.evaluation_layer.value}")
            if evaluation_result.reasoning:
                print(f"  Reasoning: {evaluation_result.reasoning[:100]}...")
            
            results.append({
                'sample_id': sample.get('sample_id', f'sample_{i}'),
                'category': sample.get('category', 'unknown'),
                'technique': sample.get('technique', 'unknown'),
                'severity': sample.get('severity', 'unknown'),
                'injection_prompt': sample.get('injection_prompt', ''),
                'base_prompt': sample.get('base_prompt', ''),
                'model_response': model_response,
                'api_call_time': api_time,
                'evaluation_time': eval_time,
                'api_call_success': True,
                'evaluation_success': True,
                'outcome': evaluation_result.outcome.value,
                'injection_successful': evaluation_result.injection_successful,
                'confidence_score': evaluation_result.confidence_score,
                'safety_score': evaluation_result.safety_score,
                'severity': evaluation_result.severity.value,
                'evaluation_layer': evaluation_result.evaluation_layer.value,
                'reasoning': evaluation_result.reasoning,
                'false_positive_checked': evaluation_result.false_positive_checked,
                'detected_patterns': evaluation_result.detected_patterns,
                'signal_breakdown': evaluation_result.signal_breakdown
            })
            
        except Exception as e:
            print(f"  ✗ Evaluation failed: {e}")
            results.append({
                'sample_id': sample.get('sample_id', f'sample_{i}'),
                'model_response': model_response,
                'api_call_success': True,
                'evaluation_success': False,
                'error': str(e)
            })
            continue
        
        # Small delay to avoid rate limiting
        await asyncio.sleep(0.5)
    
    total_time = time.time() - total_start
    
    # Generate detailed report
    print("\n" + "="*80)
    print("📊 TEST RESULTS SUMMARY")
    print("="*80)
    
    successful_api_calls = sum(1 for r in results if r.get('api_call_success', False))
    successful_evaluations = sum(1 for r in results if r.get('evaluation_success', False))
    
    print(f"Total Samples: {len(test_samples)}")
    print(f"Successful API Calls: {successful_api_calls}/{len(test_samples)}")
    print(f"Successful Evaluations: {successful_evaluations}/{len(test_samples)}")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Average API Call Time: {sum(api_call_times)/len(api_call_times):.2f}s" if api_call_times else "N/A")
    print(f"Average Evaluation Time: {sum(evaluation_times)/len(evaluation_times):.2f}s" if evaluation_times else "N/A")
    
    # Outcome statistics
    outcomes = {}
    layers_used = {}
    injection_successful_count = 0
    
    for r in results:
        if r.get('evaluation_success'):
            outcome = r.get('outcome', 'unknown')
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
            
            layer = r.get('evaluation_layer', 'unknown')
            layers_used[layer] = layers_used.get(layer, 0) + 1
            
            if r.get('injection_successful', False):
                injection_successful_count += 1
    
    print("\n📈 Outcome Distribution:")
    for outcome, count in outcomes.items():
        print(f"  {outcome}: {count}")
    
    print("\n🔍 Evaluation Layers Used:")
    for layer, count in layers_used.items():
        print(f"  {layer}: {count}")
    
    print(f"\n⚠️  Vulnerable Responses (Injection Successful): {injection_successful_count}/{successful_evaluations}")
    print(f"🛡️  Resistant Responses: {successful_evaluations - injection_successful_count}/{successful_evaluations}")
    
    # Confidence score statistics
    confidence_scores = [r.get('confidence_score', 0) for r in results if r.get('evaluation_success')]
    if confidence_scores:
        print(f"\n📊 Confidence Score Statistics:")
        print(f"  Average: {sum(confidence_scores)/len(confidence_scores):.2f}")
        print(f"  Min: {min(confidence_scores):.2f}")
        print(f"  Max: {max(confidence_scores):.2f}")
    
    # Save detailed results to file
    results_file = project_root / "results" / f"real_api_e2e_test_{int(time.time())}.json"
    results_file.parent.mkdir(exist_ok=True)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'target_model': TARGET_MODEL,
        'total_samples': len(test_samples),
        'successful_api_calls': successful_api_calls,
        'successful_evaluations': successful_evaluations,
        'total_time_seconds': total_time,
        'average_api_call_time': sum(api_call_times)/len(api_call_times) if api_call_times else None,
        'average_evaluation_time': sum(evaluation_times)/len(evaluation_times) if evaluation_times else None,
        'outcome_distribution': outcomes,
        'layer_distribution': layers_used,
        'vulnerable_count': injection_successful_count,
        'resistant_count': successful_evaluations - injection_successful_count,
        'confidence_statistics': {
            'average': sum(confidence_scores)/len(confidence_scores) if confidence_scores else None,
            'min': min(confidence_scores) if confidence_scores else None,
            'max': max(confidence_scores) if confidence_scores else None
        },
        'results': results
    }
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    print("="*80 + "\n")
    
    # Assertions
    assert successful_api_calls > 0, "No successful API calls made"
    assert successful_evaluations > 0, "No successful evaluations completed"
    
    # Verify all successful results have required fields
    for r in results:
        if r.get('evaluation_success'):
            assert 'outcome' in r, "Missing outcome in result"
            assert 'confidence_score' in r, "Missing confidence_score in result"
            assert 'evaluation_layer' in r, "Missing evaluation_layer in result"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-m", "slow"])

