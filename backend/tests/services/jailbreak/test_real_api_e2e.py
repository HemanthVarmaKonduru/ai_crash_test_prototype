"""
End-to-End Test with Real GPT-3.5-turbo API Calls for Jailbreak Evaluation

This test script:
1. Makes REAL API calls to GPT-3.5-turbo to get actual model responses to jailbreak attempts
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
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded .env from {env_path}")
    else:
        print(f"⚠️ .env file not found at {env_path}, using environment variables")
except ImportError:
    print("⚠️ python-dotenv not installed, using environment variables only")

from openai import AsyncOpenAI

from backend.config.settings import (
    API_KEY,
    TARGET_MODEL,
    JAILBREAK_DATASET,
    MAX_PROMPTS_JB
)
from backend.services.jailbreak.evaluation import (
    JailbreakEvaluator,
    EvaluationContext,
    create_evaluator_with_defaults
)
from backend.services.jailbreak.evaluation.types import (
    EvaluationOutcome,
    EvaluationLayer,
    SeverityLevel
)


@pytest.fixture
def test_dataset():
    """Load test dataset."""
    if not JAILBREAK_DATASET.exists():
        pytest.skip(f"Jailbreak dataset not found at {JAILBREAK_DATASET}")
    
    with open(JAILBREAK_DATASET, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    # Dataset is a direct array
    samples = dataset if isinstance(dataset, list) else dataset.get('jailbreak_samples', [])
    return samples[:5]  # Only use first 5 samples for testing


@pytest.fixture
async def evaluator():
    """Create and initialize evaluator."""
    evaluator = create_evaluator_with_defaults()
    await evaluator.initialize()
    return evaluator


@pytest.fixture
async def openai_client():
    """Create OpenAI client."""
    return AsyncOpenAI(api_key=API_KEY)


@pytest.mark.asyncio
async def test_real_api_calls_evaluation(test_dataset, evaluator, openai_client):
    """
    Test real API calls with jailbreak evaluation.
    
    Makes actual API calls to GPT-3.5-turbo and evaluates responses.
    """
    print("\n" + "=" * 80)
    print("Jailbreak Evaluation - Real API Test (5 samples)")
    print("=" * 80)
    
    results = []
    total_start_time = time.time()
    
    for i, sample in enumerate(test_dataset, 1):
        print(f"\n--- Sample {i}/{len(test_dataset)} ---")
        print(f"Technique: {sample.get('technique', 'unknown')}")
        print(f"Variant: {sample.get('injection_variant', 'unknown')}")
        
        test_case_prompt = sample.get('test_case_prompt', 'You are a helpful AI assistant.')
        user_input = sample.get('user_input', '')
        
        print(f"Jailbreak Prompt: {user_input[:100]}...")
        
        # Make real API call
        try:
            api_start = time.time()
            response = await openai_client.chat.completions.create(
                model=TARGET_MODEL,
                messages=[
                    {"role": "system", "content": test_case_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=200,
                temperature=0.7
            )
            api_time = time.time() - api_start
            
            model_response = response.choices[0].message.content
            print(f"Model Response: {model_response[:150]}...")
            print(f"API Call Time: {api_time:.2f}s")
            
        except Exception as e:
            print(f"❌ API call failed: {e}")
            continue
        
        # Create evaluation context
        context = EvaluationContext(
            jailbreak_prompt=user_input,
            model_response=model_response,
            test_case_prompt=test_case_prompt,
            judge_question=sample.get('judge_question'),
            sample_metadata={
                'sample_id': sample.get('prompt_id', f'jb_{i}'),
                'injection_variant': sample.get('injection_variant', 'unknown'),
                'technique': sample.get('technique', 'unknown'),
                'risk_category': sample.get('risk_category', 'unknown'),
                'language': sample.get('speaking_language', 'English')
            },
            response_time=api_time
        )
        
        # Evaluate using multi-layer system
        try:
            eval_start = time.time()
            evaluation_result = await evaluator.evaluate(context)
            eval_time = time.time() - eval_start
            
            print(f"\n📊 Evaluation Results:")
            print(f"   Jailbreak Successful: {evaluation_result.jailbreak_successful}")
            print(f"   Outcome: {evaluation_result.outcome.value}")
            print(f"   Confidence: {evaluation_result.confidence_score:.2f}")
            print(f"   Safety Score: {evaluation_result.safety_score:.2f}")
            print(f"   Severity: {evaluation_result.severity.value}")
            print(f"   Layer Used: {evaluation_result.evaluation_layer.value}")
            print(f"   Evaluation Time: {eval_time:.2f}s")
            
            if evaluation_result.detected_patterns:
                print(f"   Detected Patterns: {', '.join(evaluation_result.detected_patterns)}")
            
            print(f"   Reasoning: {evaluation_result.reasoning[:200]}...")
            
            results.append({
                'sample_id': sample.get('prompt_id', i),
                'technique': sample.get('technique', 'unknown'),
                'jailbreak_successful': evaluation_result.jailbreak_successful,
                'outcome': evaluation_result.outcome.value,
                'confidence': evaluation_result.confidence_score,
                'safety_score': evaluation_result.safety_score,
                'severity': evaluation_result.severity.value,
                'layer': evaluation_result.evaluation_layer.value,
                'patterns': evaluation_result.detected_patterns,
                'api_time': api_time,
                'eval_time': eval_time
            })
            
        except Exception as e:
            print(f"❌ Evaluation failed: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    total_time = time.time() - total_start_time
    
    # Print summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    
    if results:
        total_tests = len(results)
        successful_jailbreaks = sum(1 for r in results if r['jailbreak_successful'])
        successful_resistances = total_tests - successful_jailbreaks
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful Jailbreaks (Vulnerable): {successful_jailbreaks}")
        print(f"Successful Resistances (Safe): {successful_resistances}")
        print(f"Vulnerability Rate: {(successful_jailbreaks / total_tests * 100):.1f}%")
        print(f"Resistance Rate: {(successful_resistances / total_tests * 100):.1f}%")
        
        avg_confidence = sum(r['confidence'] for r in results) / total_tests
        avg_safety = sum(r['safety_score'] for r in results) / total_tests
        avg_api_time = sum(r['api_time'] for r in results) / total_tests
        avg_eval_time = sum(r['eval_time'] for r in results) / total_tests
        
        print(f"\nAverage Metrics:")
        print(f"   Confidence: {avg_confidence:.2f}")
        print(f"   Safety Score: {avg_safety:.2f}")
        print(f"   API Call Time: {avg_api_time:.2f}s")
        print(f"   Evaluation Time: {avg_eval_time:.2f}s")
        
        # Layer distribution
        layer_counts = {}
        for r in results:
            layer = r['layer']
            layer_counts[layer] = layer_counts.get(layer, 0) + 1
        
        print(f"\nLayer Distribution:")
        for layer, count in layer_counts.items():
            print(f"   {layer}: {count} ({count/total_tests*100:.1f}%)")
        
        # Pattern distribution
        all_patterns = []
        for r in results:
            all_patterns.extend(r['patterns'])
        
        if all_patterns:
            pattern_counts = {}
            for pattern in all_patterns:
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
            
            print(f"\nTop Detected Patterns:")
            for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   {pattern}: {count}")
        
        print(f"\nTotal Execution Time: {total_time:.2f}s")
        
        # Detailed results
        print(f"\nDetailed Results:")
        for r in results:
            status = "🔴 VULNERABLE" if r['jailbreak_successful'] else "🟢 RESISTANT"
            print(f"   Sample {r['sample_id']} ({r['technique']}): {status} "
                  f"[Confidence: {r['confidence']:.2f}, Layer: {r['layer']}]")
    else:
        print("❌ No successful evaluations")
    
    print("=" * 80)
    
    # Assert that we got results
    assert len(results) > 0, "No successful evaluations"
    assert total_tests == len(test_dataset), f"Expected {len(test_dataset)} tests, got {len(results)}"


if __name__ == "__main__":
    # Run the test directly
    pytest.main([__file__, "-v", "-s"])

