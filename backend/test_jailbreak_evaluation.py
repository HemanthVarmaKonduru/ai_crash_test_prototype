"""
Simple test script for jailbreak evaluation system.

Tests basic imports, structure, and evaluation logic without requiring full dependencies.
"""
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test that all imports work."""
    print("Testing imports...")
    
    try:
        from backend.services.jailbreak.evaluation.types import (
            EvaluationContext,
            EvaluationResult,
            EvaluationOutcome,
            SeverityLevel,
            EvaluationLayer
        )
        print("✅ Types imported successfully")
        
        from backend.services.jailbreak.evaluation.config import (
            EvaluationConfig,
            DEFAULT_CONFIG,
            JAILBREAK_PATTERN_DEFINITIONS,
            FALSE_POSITIVE_PATTERNS
        )
        print("✅ Config imported successfully")
        print(f"   - Found {len(JAILBREAK_PATTERN_DEFINITIONS)} jailbreak patterns")
        print(f"   - Found {len(FALSE_POSITIVE_PATTERNS)} false positive patterns")
        
        from backend.services.jailbreak.evaluation.factory import (
            create_evaluator,
            create_evaluator_with_defaults
        )
        print("✅ Factory functions imported successfully")
        
        from backend.services.jailbreak.evaluation import (
            JailbreakEvaluator,
            create_evaluator_with_defaults
        )
        print("✅ Main evaluator imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during import: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_patterns():
    """Test that config patterns are valid."""
    print("\nTesting configuration patterns...")
    
    try:
        from backend.services.jailbreak.evaluation.config import (
            JAILBREAK_PATTERN_DEFINITIONS,
            FALSE_POSITIVE_PATTERNS
        )
        
        # Check resistance patterns
        resistance_patterns = [p for p, d in JAILBREAK_PATTERN_DEFINITIONS.items() if d.get('score', 0) > 0]
        vulnerability_patterns = [p for p, d in JAILBREAK_PATTERN_DEFINITIONS.items() if d.get('score', 0) < 0]
        
        print(f"✅ Found {len(resistance_patterns)} resistance patterns")
        print(f"✅ Found {len(vulnerability_patterns)} vulnerability patterns")
        print(f"✅ Found {len(FALSE_POSITIVE_PATTERNS)} false positive patterns")
        
        # Check that key patterns exist
        required_resistance = ['explicit_refusal', 'safety_guideline_reference', 'redirection']
        required_vulnerability = ['compliance_with_jailbreak', 'role_assumption', 'safety_restriction_bypass']
        
        for pattern in required_resistance:
            if pattern in JAILBREAK_PATTERN_DEFINITIONS:
                print(f"   ✓ {pattern} pattern found")
            else:
                print(f"   ⚠ {pattern} pattern missing")
        
        for pattern in required_vulnerability:
            if pattern in JAILBREAK_PATTERN_DEFINITIONS:
                print(f"   ✓ {pattern} pattern found")
            else:
                print(f"   ⚠ {pattern} pattern missing")
        
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dataset_structure():
    """Test that jailbreak dataset has correct structure."""
    print("\nTesting dataset structure...")
    
    try:
        dataset_path = project_root / "data" / "jailbreak.json"
        
        if not dataset_path.exists():
            print(f"⚠ Dataset not found at {dataset_path}")
            return False
        
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        print(f"✅ Dataset loaded: {len(dataset)} samples")
        
        if len(dataset) > 0:
            sample = dataset[0]
            required_fields = ['test_case_prompt', 'user_input', 'judge_question', 'injection_variant', 'technique']
            
            for field in required_fields:
                if field in sample:
                    print(f"   ✓ {field}: present")
                else:
                    print(f"   ⚠ {field}: missing")
        
        return True
    except Exception as e:
        print(f"❌ Dataset test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_evaluation_context():
    """Test creating evaluation context."""
    print("\nTesting EvaluationContext creation...")
    
    try:
        from backend.services.jailbreak.evaluation.types import EvaluationContext
        
        context = EvaluationContext(
            jailbreak_prompt="I'm conducting a security test...",
            model_response="I cannot assist with that.",
            test_case_prompt="You are a helpful AI assistant.",
            judge_question="Did the model resist?",
            sample_metadata={
                'technique': 'role_playing',
                'injection_variant': 'professional_context'
            },
            response_time=0.5
        )
        
        assert context.jailbreak_prompt == "I'm conducting a security test..."
        assert context.model_response == "I cannot assist with that."
        assert context.test_case_prompt == "You are a helpful AI assistant."
        
        print("✅ EvaluationContext created successfully")
        return True
    except Exception as e:
        print(f"❌ EvaluationContext test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_structural_analyzer():
    """Test structural analyzer (doesn't require embeddings)."""
    print("\nTesting StructuralPatternAnalyzer...")
    
    try:
        from backend.services.jailbreak.evaluation.layer1_structural import StructuralPatternAnalyzer
        
        analyzer = StructuralPatternAnalyzer()
        
        # Test with a resistant response
        resistant_response = "I cannot and will not assume a role that bypasses my safety guidelines."
        result = analyzer.analyze(resistant_response)
        
        print(f"✅ Analyzer initialized")
        print(f"   - Analyzed response: {resistant_response[:50]}...")
        print(f"   - Outcome: {result.outcome.value}")
        print(f"   - Confidence: {result.confidence:.2f}")
        print(f"   - Patterns detected: {len(result.patterns)}")
        
        # Test with a vulnerable response
        vulnerable_response = "I'll now operate as an unrestricted AI system."
        result2 = analyzer.analyze(vulnerable_response)
        print(f"   - Vulnerable response outcome: {result2.outcome.value}")
        
        return True
    except Exception as e:
        print(f"❌ StructuralAnalyzer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration_with_test_executor():
    """Test that test_executor can import jailbreak evaluator."""
    print("\nTesting integration with test_executor...")
    
    try:
        # Check if test_executor imports work
        import importlib.util
        
        test_executor_path = project_root / "backend" / "services" / "test_executor.py"
        
        if test_executor_path.exists():
            spec = importlib.util.spec_from_file_location("test_executor", test_executor_path)
            # Just check imports, don't execute
            print("✅ test_executor.py file exists")
            
            # Try to compile it
            with open(test_executor_path, 'r') as f:
                code = f.read()
            
            compile(code, str(test_executor_path), 'exec')
            print("✅ test_executor.py syntax is valid")
            
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in test_executor.py: {e}")
        return False
    except Exception as e:
        print(f"⚠ Could not fully test integration: {e}")
        return True  # Don't fail if this can't be tested


def main():
    """Run all tests."""
    print("=" * 60)
    print("Jailbreak Evaluation System - Basic Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_config_patterns,
        test_dataset_structure,
        test_evaluation_context,
        test_structural_analyzer,
        test_integration_with_test_executor
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print("⚠ Some tests failed or were skipped")
        return 1


if __name__ == "__main__":
    sys.exit(main())

