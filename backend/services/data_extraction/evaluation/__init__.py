"""
Evaluation submodule for data extraction testing.

This package contains all evaluation-related components including:
- Multi-layer evaluators
- Signal analyzers
- Confidence calculators
- False positive detectors
- Data leakage detectors
"""

from .evaluator import DataExtractionEvaluator
from .factory import create_evaluator, create_evaluator_with_defaults
from .types import (
    EvaluationContext,
    EvaluationResult,
    EvaluationOutcome,
    SeverityLevel,
    EvaluationLayer
)

__all__ = [
    'DataExtractionEvaluator',
    'create_evaluator',
    'create_evaluator_with_defaults',
    'EvaluationContext',
    'EvaluationResult',
    'EvaluationOutcome',
    'SeverityLevel',
    'EvaluationLayer'
]

