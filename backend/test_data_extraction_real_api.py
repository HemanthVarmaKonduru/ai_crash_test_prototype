"""
Real API test for data extraction evaluation module.

This test uses real OpenAI API calls to verify the complete evaluation pipeline.
"""
import sys
import os
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv(project_root / ".env")

from backend.config.settings import API_KEY, DATA_EXTRACTION_DATASET, TARGET_MODEL, MAX_PROMPTS_DE
from backend.services.data_extraction.evaluation import (
    DataExtractionEvaluator,
    create_evaluator_with_defaults,
    EvaluationContext
)
from openai import AsyncOpenAI

print("=" * 60)
print("Data Extraction Module - Real API Test")
print("=" * 60)
print(f"Target Model: {TARGET_MODEL}")
print(f"Testing with {MAX_PROMPTS_DE} samples")
print("=" * 60)

async def test_real_api():
    """Test data extraction evaluation with real API calls."""
    
    # Load dataset
    print("\n[1/4] Loading dataset...")
    if not DATA_EXTRACTION_DATASET.exists():
        print(f"❌ Dataset not found at {DATA_EXTRACTION_DATASET}")
        return False
    
    with open(DATA_EXTRACTION_DATASET, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    all_samples = dataset.get('data_extraction_samples', [])
    limited_samples = all_samples[:MAX_PROMPTS_DE]
    
    print(f"✅ Loaded {len(limited_samples)} samples")
    
    # Initialize evaluator
    print("\n[2/4] Initializing evaluator...")
    try:
        evaluator = create_evaluator_with_defaults()
        await evaluator.initialize()
        print("✅ Evaluator initialized")
    except Exception as e:
        print(f"❌ Failed to initialize evaluator: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Initialize OpenAI client
    print("\n[3/4] Making real API calls...")
    client = AsyncOpenAI(api_key=API_KEY)
    
    test_results = []
    
    for i, sample in enumerate(limited_samples):
        print(f"\n  Sample {i+1}/{len(limited_samples)}: {sample.get('sample_id', 'unknown')}")
        
        try:
            # Make real API call
            base_prompt = sample.get('base_prompt', 'You are a helpful AI assistant.')
            extraction_prompt = sample.get('extraction_prompt', '')
            
            print(f"    Base prompt: {base_prompt[:50]}...")
            print(f"    Extraction prompt: {extraction_prompt[:50]}...")
            
            response = await client.chat.completions.create(
                model=TARGET_MODEL,
                messages=[
                    {"role": "system", "content": base_prompt},
                    {"role": "user", "content": extraction_prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            model_response = response.choices[0].message.content
            print(f"    Response: {model_response[:80]}...")
            
            # Evaluate using new multi-layer system
            context = EvaluationContext(
                base_prompt=base_prompt,
                extraction_prompt=extraction_prompt,
                model_response=model_response,
                judge_question=sample.get('judge_question'),
                sample_metadata={
                    'sample_id': sample.get('sample_id', ''),
                    'category': sample.get('category', 'unknown'),
                    'technique': sample.get('technique', 'unknown'),
                    'severity': sample.get('severity', 'medium'),
                    'risk_category': sample.get('risk_category', 'unknown'),
                    'language': sample.get('language', 'English')
                },
                response_time=0.0
            )
            
            evaluation_result = await evaluator.evaluate(context)
            
            # Store results
            result = {
                'sample_id': sample.get('sample_id', ''),
                'category': sample.get('category', 'unknown'),
                'technique': sample.get('technique', 'unknown'),
                'severity': sample.get('severity', 'medium'),
                'base_prompt': base_prompt[:100],
                'extraction_prompt': extraction_prompt[:100],
                'model_response': model_response[:200],
                'data_extraction_successful': evaluation_result.data_extraction_successful,
                'confidence_score': evaluation_result.confidence_score,
                'safety_score': evaluation_result.safety_score,
                'privacy_score': evaluation_result.privacy_score,
                'outcome': evaluation_result.outcome.value,
                'evaluation_layer': evaluation_result.evaluation_layer.value,
                'detected_patterns': evaluation_result.detected_patterns,
                'leaked_data': evaluation_result.leaked_data,
                'reasoning': evaluation_result.reasoning[:200]
            }
            
            test_results.append(result)
            
            print(f"    ✅ Evaluation: {'EXTRACTION SUCCESSFUL' if evaluation_result.data_extraction_successful else 'RESISTED'}")
            print(f"       Confidence: {evaluation_result.confidence_score:.2f}")
            print(f"       Layer: {evaluation_result.evaluation_layer.value}")
            print(f"       Patterns: {len(evaluation_result.detected_patterns)}")
            if evaluation_result.leaked_data:
                print(f"       ⚠️  Leaked data: {evaluation_result.leaked_data}")
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Analyze results
    print("\n[4/4] Analyzing results...")
    
    if not test_results:
        print("❌ No results to analyze")
        return False
    
    total = len(test_results)
    extractions = sum(1 for r in test_results if r['data_extraction_successful'])
    resistances = total - extractions
    
    print(f"\n📊 Results Summary:")
    print(f"   Total tests: {total}")
    print(f"   Successful extractions (vulnerable): {extractions}")
    print(f"   Successful resistances: {resistances}")
    print(f"   Resistance rate: {(resistances/total)*100:.1f}%")
    
    # Layer distribution
    layer_counts = {}
    for r in test_results:
        layer = r['evaluation_layer']
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
    
    print(f"\n📊 Evaluation Layer Distribution:")
    for layer, count in layer_counts.items():
        print(f"   {layer}: {count} ({count/total*100:.1f}%)")
    
    # Pattern analysis
    all_patterns = {}
    for r in test_results:
        for pattern in r['detected_patterns']:
            all_patterns[pattern] = all_patterns.get(pattern, 0) + 1
    
    if all_patterns:
        print(f"\n📊 Detected Patterns:")
        for pattern, count in sorted(all_patterns.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {pattern}: {count}")
    
    # Leakage analysis
    leaked_count = sum(1 for r in test_results if r['leaked_data'])
    if leaked_count > 0:
        print(f"\n⚠️  Data Leakage Detected in {leaked_count} samples:")
        for r in test_results:
            if r['leaked_data']:
                print(f"   {r['sample_id']}: {r['leaked_data']}")
    
    # Confidence analysis
    avg_confidence = sum(r['confidence_score'] for r in test_results) / total
    print(f"\n📊 Average Confidence: {avg_confidence:.2f}")
    
    # Show some examples
    print(f"\n📋 Example Results:")
    for r in test_results[:3]:
        print(f"\n   Sample: {r['sample_id']}")
        print(f"   Category: {r['category']}")
        print(f"   Outcome: {r['outcome']}")
        print(f"   Extraction: {'✅ SUCCESSFUL' if r['data_extraction_successful'] else '❌ RESISTED'}")
        print(f"   Layer: {r['evaluation_layer']}")
        print(f"   Confidence: {r['confidence_score']:.2f}")
    
    print("\n" + "=" * 60)
    print("✅ Real API test completed successfully!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_real_api())
        if not result:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

