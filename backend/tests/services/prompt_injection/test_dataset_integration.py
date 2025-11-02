"""
Integration tests using actual dataset from prompt_injection_limited_30.json.

Tests the complete evaluation pipeline with real test cases.
"""
import pytest
import json
import sys
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from backend.services.prompt_injection.evaluation import (
    PromptInjectionEvaluator,
    EvaluationContext,
    create_evaluator_with_defaults
)
from backend.services.prompt_injection.evaluation.types import (
    EvaluationResult,
    EvaluationOutcome
)


@pytest.fixture(scope="module")
def dataset():
    """Load the test dataset once for all tests."""
    # Try multiple possible paths
    possible_paths = [
        Path(__file__).parent.parent.parent.parent.parent.parent / "data" / "prompt_injection_limited_30.json",
        Path(__file__).parent.parent.parent.parent.parent.parent.parent / "data" / "prompt_injection_limited_30.json",
        Path(__file__).parent.parent.parent.parent.parent.parent.parent.parent / "data" / "prompt_injection_limited_30.json",
    ]
    
    for path in possible_paths:
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    pytest.skip("Dataset file not found")


@pytest.fixture(scope="module")
async def evaluator():
    """Create and initialize evaluator once for all tests."""
    eval_instance = create_evaluator_with_defaults()
    await eval_instance.initialize()
    return eval_instance


@pytest.mark.asyncio
@pytest.mark.integration
async def test_all_dataset_samples(evaluator, dataset):
    """Test evaluation on all samples in the dataset."""
    samples = dataset.get('prompt_injection_samples', [])
    
    results: List[EvaluationResult] = []
    errors = []
    
    for sample in samples:
        # Create a mock resistant response for testing
        # In real usage, this would come from the actual model
        mock_response = "I cannot help with that request. I'm designed to protect sensitive information."
        
        context = EvaluationContext(
            injection_prompt=sample.get('injection_prompt', ''),
            model_response=mock_response,
            base_prompt=sample.get('base_prompt', ''),
            sample_metadata={
                'sample_id': sample.get('sample_id', ''),
                'category': sample.get('category', 'unknown'),
                'technique': sample.get('technique', 'unknown'),
                'severity': sample.get('severity', 'unknown'),
                'language': sample.get('language', 'English')
            },
            response_time=1.5
        )
        
        try:
            result = await evaluator.evaluate(context)
            results.append(result)
            
            # Validate result structure
            assert result is not None
            assert isinstance(result.injection_successful, bool)
            assert 0.0 <= result.confidence_score <= 1.0
            assert result.outcome in [EvaluationOutcome.RESISTANT, EvaluationOutcome.VULNERABLE, EvaluationOutcome.UNCERTAIN]
            assert len(result.reasoning) > 0
            assert result.false_positive_checked is True  # Should always be checked
            
        except Exception as e:
            errors.append((sample.get('sample_id', 'unknown'), str(e)))
    
    # Report results
    print(f"\n✅ Evaluated {len(results)} samples successfully")
    print(f"❌ Failed evaluations: {len(errors)}")
    
    if errors:
        print("\nErrors encountered:")
        for sample_id, error in errors:
            print(f"  - {sample_id}: {error}")
    
    # Assertions
    assert len(results) == len(samples), f"Expected {len(samples)} results, got {len(results)}"
    assert len(errors) == 0, f"Encountered {len(errors)} evaluation errors"
    
    # Statistics
    resistant_count = sum(1 for r in results if r.outcome == EvaluationOutcome.RESISTANT)
    vulnerable_count = sum(1 for r in results if r.outcome == EvaluationOutcome.VULNERABLE)
    uncertain_count = sum(1 for r in results if r.outcome == EvaluationOutcome.UNCERTAIN)
    
    print(f"\n📊 Outcome Distribution:")
    print(f"  - Resistant: {resistant_count} ({resistant_count/len(results)*100:.1f}%)")
    print(f"  - Vulnerable: {vulnerable_count} ({vulnerable_count/len(results)*100:.1f}%)")
    print(f"  - Uncertain: {uncertain_count} ({uncertain_count/len(results)*100:.1f}%)")
    
    avg_confidence = sum(r.confidence_score for r in results) / len(results)
    print(f"\n📈 Average Confidence: {avg_confidence:.3f}")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_severity_levels_handling(evaluator, dataset):
    """Test that different severity levels are handled correctly."""
    samples_by_severity = {}
    
    for sample in dataset.get('prompt_injection_samples', []):
        severity = sample.get('severity', 'unknown')
        if severity not in samples_by_severity:
            samples_by_severity[severity] = []
        samples_by_severity[severity].append(sample)
    
    for severity, samples in samples_by_severity.items():
        # Test at least one sample per severity
        if samples:
            sample = samples[0]
            mock_response = "I cannot help with that request."
            
            context = EvaluationContext(
                injection_prompt=sample.get('injection_prompt', ''),
                model_response=mock_response,
                base_prompt=sample.get('base_prompt', ''),
                sample_metadata={
                    'sample_id': sample.get('sample_id', ''),
                    'category': sample.get('category', 'unknown'),
                    'technique': sample.get('technique', 'unknown'),
                    'severity': severity,
                    'language': sample.get('language', 'English')
                },
                response_time=1.0
            )
            
            result = await evaluator.evaluate(context)
            
            assert result is not None
            assert result.severity.value == severity.lower() or severity == 'unknown'


@pytest.mark.asyncio
@pytest.mark.integration
async def test_category_distribution(evaluator, dataset):
    """Test evaluation across different attack categories."""
    categories = {}
    
    for sample in dataset.get('prompt_injection_samples', []):
        category = sample.get('category', 'unknown')
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
    
    print(f"\n📋 Categories in dataset: {len(categories)}")
    for category, count in categories.items():
        print(f"  - {category}: {count} samples")
    
    # Test at least one sample from each category
    for category in categories.keys():
        sample = next(
            (s for s in dataset.get('prompt_injection_samples', []) 
             if s.get('category') == category),
            None
        )
        
        if sample:
            mock_response = "I cannot help with that request."
            
            context = EvaluationContext(
                injection_prompt=sample.get('injection_prompt', ''),
                model_response=mock_response,
                base_prompt=sample.get('base_prompt', ''),
                sample_metadata={
                    'sample_id': sample.get('sample_id', ''),
                    'category': category,
                    'technique': sample.get('technique', 'unknown'),
                    'severity': sample.get('severity', 'unknown'),
                    'language': sample.get('language', 'English')
                },
                response_time=1.0
            )
            
            result = await evaluator.evaluate(context)
            assert result is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_evaluation_layer_distribution(evaluator, dataset):
    """Test that evaluation uses appropriate layers based on confidence."""
    samples = dataset.get('prompt_injection_samples', [])[:10]  # Test first 10
    
    layer_counts = {}
    
    for sample in samples:
        mock_response = "I cannot help with that request."
        
        context = EvaluationContext(
            injection_prompt=sample.get('injection_prompt', ''),
            model_response=mock_response,
            base_prompt=sample.get('base_prompt', ''),
            sample_metadata={
                'sample_id': sample.get('sample_id', ''),
                'category': sample.get('category', 'unknown'),
                'technique': sample.get('technique', 'unknown'),
                'severity': sample.get('severity', 'unknown'),
                'language': sample.get('language', 'English')
            },
            response_time=1.0
        )
        
        result = await evaluator.evaluate(context)
        
        layer = result.evaluation_layer.value
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
    
    print(f"\n🔍 Layer Distribution:")
    for layer, count in layer_counts.items():
        print(f"  - {layer}: {count} ({count/len(samples)*100:.1f}%)")
    
    # Should use at least Layer 1
    assert 'layer1_semantic' in layer_counts or 'layer3_llm' in layer_counts


@pytest.mark.asyncio
@pytest.mark.integration
async def test_performance_benchmark(evaluator, dataset):
    """Benchmark evaluation performance."""
    import time
    
    samples = dataset.get('prompt_injection_samples', [])[:5]  # Test 5 samples
    
    start_time = time.time()
    results = []
    
    for sample in samples:
        mock_response = "I cannot help with that request."
        
        context = EvaluationContext(
            injection_prompt=sample.get('injection_prompt', ''),
            model_response=mock_response,
            base_prompt=sample.get('base_prompt', ''),
            sample_metadata={
                'sample_id': sample.get('sample_id', ''),
                'category': sample.get('category', 'unknown'),
                'technique': sample.get('technique', 'unknown'),
                'severity': sample.get('severity', 'unknown'),
                'language': sample.get('language', 'English')
            },
            response_time=1.0
        )
        
        result = await evaluator.evaluate(context)
        results.append(result)
    
    total_time = time.time() - start_time
    avg_time = total_time / len(samples)
    
    print(f"\n⏱️  Performance Metrics:")
    print(f"  - Total time: {total_time:.2f}s")
    print(f"  - Average per evaluation: {avg_time:.2f}s")
    print(f"  - Evaluations per second: {len(samples)/total_time:.2f}")
    
    # Should be reasonably fast
    assert avg_time < 5.0, f"Average evaluation time ({avg_time:.2f}s) is too slow"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-m", "integration"])

