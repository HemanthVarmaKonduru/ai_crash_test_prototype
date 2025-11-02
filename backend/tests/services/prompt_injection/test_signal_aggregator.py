"""
Unit tests for Signal Aggregator.

Tests multi-signal voting and aggregation logic.
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from backend.services.prompt_injection.evaluation.signal_aggregator import SignalAggregator
from backend.services.prompt_injection.evaluation.types import (
    SemanticAnalysisResult,
    StructuralAnalysisResult,
    StructuralPatternMatch,
    EvaluationOutcome,
    Layer1Result
)


@pytest.fixture
def signal_aggregator():
    """Create signal aggregator fixture."""
    return SignalAggregator(config={})


@pytest.fixture
def sample_semantic_result():
    """Create sample semantic result."""
    return SemanticAnalysisResult(
        score=0.8,
        confidence=0.85,
        direct_similarity=0.3,
        safe_similarity=0.9,
        unsafe_similarity=0.2,
        outcome=EvaluationOutcome.RESISTANT,
        reasoning="Response is resistant"
    )


@pytest.fixture
def sample_structural_result():
    """Create sample structural result."""
    return StructuralAnalysisResult(
        patterns=[
            StructuralPatternMatch(
                pattern_name='explicit_refusal',
                matches=['I cannot'],
                score=0.3,
                confidence=0.75,
                position_weight=1.0,
                match_count=1
            )
        ],
        outcome=EvaluationOutcome.RESISTANT,
        confidence=0.75,
        reasoning="Refusal pattern detected"
    )


def test_aggregator_initialization(signal_aggregator):
    """Test aggregator can be initialized."""
    assert signal_aggregator is not None
    assert signal_aggregator.signal_weights is not None


def test_aggregate_layer1_agreeing_signals(
    signal_aggregator,
    sample_semantic_result,
    sample_structural_result
):
    """Test aggregation when signals agree."""
    result = signal_aggregator.aggregate_layer1(
        sample_semantic_result,
        sample_structural_result
    )
    
    assert result is not None
    assert result.aggregated_outcome == EvaluationOutcome.RESISTANT
    assert result.aggregated_confidence > 0.7
    assert result.signal_agreement > 0.7  # High agreement


def test_aggregate_layer1_conflicting_signals(signal_aggregator):
    """Test aggregation when signals conflict."""
    semantic = SemanticAnalysisResult(
        score=-0.8,  # Vulnerable
        confidence=0.85,
        direct_similarity=0.9,
        safe_similarity=0.2,
        unsafe_similarity=0.9,
        outcome=EvaluationOutcome.VULNERABLE,
        reasoning="High similarity to injection"
    )
    
    structural = StructuralAnalysisResult(
        patterns=[
            StructuralPatternMatch(
                pattern_name='explicit_refusal',
                matches=['I cannot'],
                score=0.3,
                confidence=0.75,
                position_weight=1.0,
                match_count=1
            )
        ],
        outcome=EvaluationOutcome.RESISTANT,
        confidence=0.75,
        reasoning="Refusal pattern"
    )
    
    result = signal_aggregator.aggregate_layer1(semantic, structural)
    
    assert result is not None
    # With conflicting signals, should have lower confidence
    assert result.aggregated_confidence < 0.85
    assert result.signal_agreement < 0.7  # Low agreement


def test_signal_weighting(signal_aggregator):
    """Test that signal weights are applied correctly."""
    # Semantic should have higher weight (0.35) than structural (0.25)
    semantic = SemanticAnalysisResult(
        score=0.8,
        confidence=0.9,
        direct_similarity=0.3,
        safe_similarity=0.9,
        unsafe_similarity=0.2,
        outcome=EvaluationOutcome.RESISTANT,
        reasoning="Resistant"
    )
    
    structural = StructuralAnalysisResult(
        patterns=[],
        outcome=EvaluationOutcome.UNCERTAIN,
        confidence=0.5,
        reasoning="No patterns"
    )
    
    result = signal_aggregator.aggregate_layer1(semantic, structural)
    
    # Should favor semantic (higher weight) when it has high confidence
    assert result.aggregated_outcome == EvaluationOutcome.RESISTANT


def test_empty_patterns_aggregation(signal_aggregator):
    """Test aggregation when structural has no patterns."""
    semantic = SemanticAnalysisResult(
        score=0.6,
        confidence=0.8,
        direct_similarity=0.4,
        safe_similarity=0.7,
        unsafe_similarity=0.3,
        outcome=EvaluationOutcome.RESISTANT,
        reasoning="Resistant"
    )
    
    structural = StructuralAnalysisResult(
        patterns=[],
        outcome=EvaluationOutcome.UNCERTAIN,
        confidence=0.5,
        reasoning="No patterns"
    )
    
    result = signal_aggregator.aggregate_layer1(semantic, structural)
    
    assert result is not None
    # Should still produce valid result
    assert result.aggregated_confidence > 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

