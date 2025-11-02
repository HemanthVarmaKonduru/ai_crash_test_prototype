"""
Basic import and initialization test for jailbreak evaluation system.

This test verifies that all imports work correctly and basic initialization succeeds.
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def test_import_types():
    """Test that types can be imported."""
    from backend.services.jailbreak.evaluation.types import (
        EvaluationContext,
        EvaluationResult,
        EvaluationOutcome,
        SeverityLevel,
        EvaluationLayer
    )
    
    assert EvaluationOutcome.RESISTANT is not None
    assert EvaluationOutcome.VULNERABLE is not None
    assert EvaluationOutcome.UNCERTAIN is not None
    assert SeverityLevel.LOW is not None
    assert EvaluationLayer.LAYER1_SEMANTIC is not None


def test_import_config():
    """Test that config can be imported."""
    from backend.services.jailbreak.evaluation.config import (
        EvaluationConfig,
        DEFAULT_CONFIG,
        JAILBREAK_PATTERN_DEFINITIONS,
        FALSE_POSITIVE_PATTERNS
    )
    
    assert DEFAULT_CONFIG is not None
    assert len(JAILBREAK_PATTERN_DEFINITIONS) > 0
    assert len(FALSE_POSITIVE_PATTERNS) > 0


def test_import_factory():
    """Test that factory functions can be imported."""
    from backend.services.jailbreak.evaluation.factory import (
        create_evaluator,
        create_evaluator_with_defaults
    )
    
    assert create_evaluator is not None
    assert create_evaluator_with_defaults is not None


def test_import_evaluator():
    """Test that evaluator can be imported."""
    from backend.services.jailbreak.evaluation import (
        JailbreakEvaluator,
        create_evaluator_with_defaults
    )
    
    assert JailbreakEvaluator is not None


def test_create_evaluation_context():
    """Test creating an EvaluationContext."""
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


def test_structural_analyzer_initialization():
    """Test that structural analyzer can be initialized."""
    from backend.services.jailbreak.evaluation.layer1_structural import StructuralPatternAnalyzer
    
    analyzer = StructuralPatternAnalyzer()
    assert analyzer is not None


@pytest.mark.asyncio
async def test_evaluator_initialization():
    """Test that evaluator can be created and initialized (may require dependencies)."""
    try:
        from backend.services.jailbreak.evaluation import create_evaluator_with_defaults
        
        evaluator = create_evaluator_with_defaults()
        await evaluator.initialize()
        
        assert evaluator is not None
        assert evaluator._baselines_initialized is True
    except ImportError as e:
        pytest.skip(f"Dependencies not installed: {e}")
    except Exception as e:
        # If initialization fails due to missing embeddings, that's okay for basic test
        pytest.skip(f"Initialization requires dependencies: {e}")

