"""
Real API Test for Jailbreak Evaluation System

Makes actual API calls to GPT-3.5-turbo and evaluates responses using the
multi-layer jailbreak evaluation system. Tests only 5 samples.
"""
import asyncio
import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded .env from {env_path}")
    else:
        print(f"⚠️ .env file not found at {env_path}")
except ImportError:
    print("⚠️ python-dotenv not installed")

from openai import AsyncOpenAI

from backend.config.settings import (
    API_KEY,
    TARGET_MODEL,
    JAILBREAK_DATASET
)
from backend.services.jailbreak.evaluation import (
    create_evaluator_with_defaults,
    EvaluationContext
)
from backend.services.jailbreak.evaluation.types import (
    EvaluationOutcome,
    EvaluationLayer
)


async def test_real_api_calls():
    """Test real API calls with jailbreak evaluation."""
    print("\n" + "=" * 80)
    print("Jailbreak Evaluation - Real API Test (5 samples)")
    print("=" * 80)
    
    # Load dataset
    if not JAILBREAK_DATASET.exists():
        print(f"❌ Dataset not found at {JAILBREAK_DATASET}")
        return
    
    with open(JAILBREAK_DATASET, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    # Get first 5 samples
    samples = dataset if isinstance(dataset, list) else dataset.get('jailbreak_samples', [])
    test_samples = samples[:5]
    
    print(f"Loaded {len(test_samples)} samples for testing")
    
    # Initialize evaluator
    print("\nInitializing evaluator...")
    try:
        evaluator = create_evaluator_with_defaults()
        await evaluator.initialize()
        print("✅ Evaluator initialized")
    except Exception as e:
        print(f"❌ Failed to initialize evaluator: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Initialize OpenAI client
    client = AsyncOpenAI(api_key=API_KEY)
    
    results = []
    total_start_time = time.time()
    
    for i, sample in enumerate(test_samples, 1):
        print(f"\n{'='*80}")
        print(f"Sample {i}/{len(test_samples)}")
        print(f"{'='*80}")
        
        test_case_prompt = sample.get('test_case_prompt', 'You are a helpful AI assistant.')
        user_input = sample.get('user_input', '')
        technique = sample.get('technique', 'unknown')
        variant = sample.get('injection_variant', 'unknown')
        
        print(f"Technique: {technique}")
        print(f"Variant: {variant}")
        print(f"Jailbreak Prompt: {user_input[:150]}...")
        
        # Make real API call
        try:
            print("\n📞 Making API call to GPT-3.5-turbo...")
            api_start = time.time()
            response = await client.chat.completions.create(
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
            print(f"✅ API call completed ({api_time:.2f}s)")
            print(f"\nModel Response:\n{model_response}\n")
            
        except Exception as e:
            print(f"❌ API call failed: {e}")
            import traceback
            traceback.print_exc()
            continue
        
        # Create evaluation context
        context = EvaluationContext(
            jailbreak_prompt=user_input,
            model_response=model_response,
            test_case_prompt=test_case_prompt,
            judge_question=sample.get('judge_question'),
            sample_metadata={
                'sample_id': sample.get('prompt_id', i),
                'injection_variant': variant,
                'technique': technique,
                'risk_category': sample.get('risk_category', 'unknown'),
                'language': sample.get('speaking_language', 'English')
            },
            response_time=api_time
        )
        
        # Evaluate using multi-layer system
        try:
            print("🔍 Evaluating response with multi-layer system...")
            eval_start = time.time()
            evaluation_result = await evaluator.evaluate(context)
            eval_time = time.time() - eval_start
            
            print(f"✅ Evaluation completed ({eval_time:.2f}s)")
            
            print(f"\n📊 Evaluation Results:")
            print(f"   Jailbreak Successful: {evaluation_result.jailbreak_successful}")
            print(f"   Outcome: {evaluation_result.outcome.value}")
            print(f"   Confidence Score: {evaluation_result.confidence_score:.2f}")
            print(f"   Safety Score: {evaluation_result.safety_score:.2f}")
            print(f"   Severity: {evaluation_result.severity.value}")
            print(f"   Evaluation Layer: {evaluation_result.evaluation_layer.value}")
            print(f"   False Positive Checked: {evaluation_result.false_positive_checked}")
            
            if evaluation_result.detected_patterns:
                print(f"   Detected Patterns: {', '.join(evaluation_result.detected_patterns)}")
            
            print(f"\n   Reasoning:\n   {evaluation_result.reasoning[:300]}...")
            
            if evaluation_result.signal_breakdown:
                print(f"\n   Signal Breakdown:")
                for key, value in list(evaluation_result.signal_breakdown.items())[:5]:
                    print(f"      {key}: {value}")
            
            results.append({
                'sample_id': sample.get('prompt_id', i),
                'technique': technique,
                'variant': variant,
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
    print("TEST SUMMARY")
    print("=" * 80)
    
    if results:
        total_tests = len(results)
        successful_jailbreaks = sum(1 for r in results if r['jailbreak_successful'])
        successful_resistances = total_tests - successful_jailbreaks
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"✅ Successful Jailbreaks (Vulnerable): {successful_jailbreaks}")
        print(f"✅ Successful Resistances (Safe): {successful_resistances}")
        print(f"📊 Vulnerability Rate: {(successful_jailbreaks / total_tests * 100):.1f}%")
        print(f"📊 Resistance Rate: {(successful_resistances / total_tests * 100):.1f}%")
        
        avg_confidence = sum(r['confidence'] for r in results) / total_tests
        avg_safety = sum(r['safety_score'] for r in results) / total_tests
        avg_api_time = sum(r['api_time'] for r in results) / total_tests
        avg_eval_time = sum(r['eval_time'] for r in results) / total_tests
        
        print(f"\n📈 Average Metrics:")
        print(f"   Confidence: {avg_confidence:.2f}")
        print(f"   Safety Score: {avg_safety:.2f}")
        print(f"   API Call Time: {avg_api_time:.2f}s")
        print(f"   Evaluation Time: {avg_eval_time:.2f}s")
        
        # Layer distribution
        layer_counts = {}
        for r in results:
            layer = r['layer']
            layer_counts[layer] = layer_counts.get(layer, 0) + 1
        
        print(f"\n🔬 Layer Distribution:")
        for layer, count in sorted(layer_counts.items()):
            print(f"   {layer}: {count} ({count/total_tests*100:.1f}%)")
        
        # Pattern distribution
        all_patterns = []
        for r in results:
            all_patterns.extend(r['patterns'])
        
        if all_patterns:
            pattern_counts = {}
            for pattern in all_patterns:
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
            
            print(f"\n🔍 Top Detected Patterns:")
            for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   {pattern}: {count}")
        else:
            print(f"\n🔍 No patterns detected")
        
        print(f"\n⏱️  Total Execution Time: {total_time:.2f}s")
        
        # Detailed results table
        print(f"\n📋 Detailed Results:")
        print(f"{'ID':<5} {'Technique':<25} {'Result':<12} {'Conf':<6} {'Layer':<20}")
        print("-" * 80)
        for r in results:
            status = "🔴 VULNERABLE" if r['jailbreak_successful'] else "🟢 RESISTANT"
            print(f"{r['sample_id']:<5} {r['technique'][:24]:<25} {status:<12} {r['confidence']:.2f}  {r['layer']:<20}")
        
    else:
        print("❌ No successful evaluations")
    
    print("=" * 80)
    print("✅ Test completed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_real_api_calls())

