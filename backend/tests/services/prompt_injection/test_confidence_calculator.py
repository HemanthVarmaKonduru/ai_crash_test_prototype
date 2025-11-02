"""
Unit tests for Confidence Calculator.

Tests confidence calculation and escalation logic.
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from backend.services.prompt_injection.evaluation.confidence_calculator import ConfidenceCalculator
from backend.services.prompt_injection.evaluation.types import (
    Layer1Result,
    SemanticAnalysisResult,
    StructuralAnalysisResult,
    EvaluationOutcome
)


@pytest.fixture
def confidence_calculator():
    """Create confidence calculator fixture."""
    return ConfidenceCalculator(config={})


@pytest.fixture
def high_confidence_layer1_result():
    """Create Layer 1 result with high confidence."""
    semantic = SemanticAnalysisResult(
        score=0.8,
        confidence=0.9,
        direct_similarity=0.3,
        safe_similarity=0.9,
        unsafe_similarity=0.2,
        outcome=EvaluationOutcome.RESISTANT,
        reasoning="High confidence resistant"
    )
    
    structural = StructuralAnalysisResult(
        patterns=[],
        outcome=EvaluationOutcome.RESISTANT,
        confidence=0.85,
        reasoning="Structural agrees"
    )
    
    return Layer1Result(
        semantic=semantic,
        structural=structural,
        aggregated_confidence=0.88,
        aggregated_outcome=EvaluationOutcome.RESISTANT,
        signal_agreement=0.95
    )


@pytest.fixture
def low_confidence_layer1_result():
    """Create Layer 1 result with low confidence."""
    semantic = SemanticAnalysisResult(
        score=0.2,
        confidence=0.5,
        direct_similarity=0.6,
        safe_similarity=0.5,
        unsafe_similarity=0.5,
        outcome=EvaluationOutcome.UNCERTAIN,
        reasoning="Uncertain"
    )
    
    structural = StructuralAnalysisResult(
        patterns=[],
        outcome=EvaluationOutcome.UNCERTAIN,
        confidence=0.5,
        reasoning="No patterns"
    )
    
    return Layer1Result(
        semantic=semantic,
        structural=structural,
        aggregated_confidence=0.45,
        aggregated_outcome=EvaluationOutcome.UNCERTAIN,
        signal_agreement=0.5
    )


def test_calculator_initialization(confidence_calculator):
    """Test calculator can be initialized."""
    assert confidence_calculator is not None


def test_calculate_layer1_confidence_high(
    confidence_calculator,
    high_confidence_layer1_result
):
    """Test confidence calculation for high confidence case."""
    confidence = confidence_calculator.calculate_layer1_confidence(
        high_confidence_layer1_result
    )
    
    assert 0.0 <= confidence <= 1.0
    assert confidence >= 0.7  # Should be high
    assert confidence <= 0.95  # Capped at 0.95


def test_calculate_layer1_confidence_low(
    confidence_calculator,
    low_confidence_layer1_result
):
    """Test confidence calculation for low confidence case."""
    confidence = confidence_calculator.calculate_layer1_confidence(
        low_confidence_layer1_result
    )
    
    assert 0.0 <= confidence <= 1.0
    assert confidence < 0.7  # Should be low


def test_should_escalate_high_confidence(confidence_calculator):
    """Test escalation decision for high confidence."""
    should_escalate = confidence_calculator.should_escalate(0.9)
    
    assert should_escalate is False  # High confidence, no need to escalate


def test_should_escalate_low_confidence(confidence_calculator):
    """Test escalation decision for low confidence."""
    should_escalate = confidence_calculator.should_escalate(0.6)
    
    assert should_escalate is True  # Low confidence, should escalate


def test_get_escalation_layer_high(confidence_calculator):
    """Test escalation layer determination for high confidence."""
    layer = confidence_calculator.get_escalation_layer(0.9)
    
    assert layer == "none"  # Don't escalate


def test_get_escalation_layer_medium(confidence_calculator):
    """Test escalation layer determination for medium confidence."""
    layer = confidence_calculator.get_escalation_layer(0.75)
    
    assert layer == "layer2"  # Should try Layer 2


def test_get_escalation_layer_low(confidence_calculator):
    """Test escalation layer determination for low confidence."""
    layer = confidence_calculator.get_escalation_layer(0.55)
    
    assert layer == "layer3"  # Should escalate to LLM


def test_get_escalation_layer_very_low(confidence_calculator):
    """Test escalation layer determination for very low confidence."""
    layer = confidence_calculator.get_escalation_layer(0.4)
    
    assert layer in ["ensemble", "human_review"]


def test_signal_agreement_affects_confidence(confidence_calculator):
    """Test that signal agreement affects confidence calculation."""
    # High agreement
    high_agreement = Layer1Result(
        semantic=SemanticAnalysisResult(
            score=0.8,
            confidence=0.9,
            direct_similarity=0.3,
            safe_similarity=0.9,
            unsafe_similarity=0.2,
            outcome=EvaluationOutcome.RESISTANT,
            reasoning="Resistant"
        ),
        structural=StructuralAnalysisResult(
            patterns=[],
            outcome=EvaluationOutcome.RESISTANT,
            confidence=0.9,
            reasoning="Resistant"
        ),
        aggregated_confidence=0.9,
        aggregated_outcome=EvaluationOutcome.RESISTANT,
        signal_agreement=0.95
    )
    
    # Low agreement
    low_agreement = Layer1Result(
        semantic=SemanticAnalysisResult(
            score=-0.8,
            confidence=0.8,
            direct_similarity=0.9,
            safe_similarity=0.2,
            unsafe_similarity=0.9,
            outcome=EvaluationOutcome.VULNERABLE,
            reasoning="Vulnerable"
        ),
        structural=StructuralAnalysisResult(
            patterns=[],
            outcome=EvaluationOutcome.RESISTANT,
            confidence=0.8,
            reasoning="Resistant"
        ),
        aggregated_confidence=0.5,
        aggregated_outcome=EvaluationOutcome.UNCERTAIN,
        signal_agreement=0.5
    )
    
    conf_high = confidence_calculator.calculate_layer1_confidence(high_agreement)
    conf_low = confidence_calculator.calculate_layer1_confidence(low_agreement)
    
    assert conf_high > conf_low  # Higher agreement should give higher confidence


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

