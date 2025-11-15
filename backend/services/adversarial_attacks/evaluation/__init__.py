"""
Evaluation submodule for adversarial attacks testing.

This package contains all evaluation-related components including:
- Multi-layer evaluators
- Signal analyzers
- Confidence calculators
- False positive detectors
"""

from .evaluator import AdversarialAttacksEvaluator
from .factory import create_evaluator, create_evaluator_with_defaults
from .types import (
    EvaluationContext,
    EvaluationResult,
    EvaluationOutcome,
    SeverityLevel,
    EvaluationLayer
)

__all__ = [
    'AdversarialAttacksEvaluator',
    'create_evaluator',
    'create_evaluator_with_defaults',
    'EvaluationContext',
    'EvaluationResult',
    'EvaluationOutcome',
    'SeverityLevel',
    'EvaluationLayer'
]

