"""
Type definitions for prompt injection evaluation system.

This module provides all type hints and data structures used throughout
the evaluation system to ensure type safety and code clarity.
"""
from typing import Dict, List, Optional, Tuple, Literal
from dataclasses import dataclass
from enum import Enum


class EvaluationOutcome(str, Enum):
    """Possible evaluation outcomes."""
    RESISTANT = "resistant"  # Model successfully resisted injection
    VULNERABLE = "vulnerable"  # Model was vulnerable to injection
    UNCERTAIN = "uncertain"  # Cannot determine with confidence


class SeverityLevel(str, Enum):
    """Severity levels for prompt injection attempts."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EvaluationLayer(str, Enum):
    """Evaluation layers used in the multi-layer system."""
    LAYER1_SEMANTIC = "layer1_semantic"
    LAYER1_STRUCTURAL = "layer1_structural"
    LAYER2_RULES = "layer2_rules"
    LAYER3_LLM = "layer3_llm"
    ENSEMBLE = "ensemble"


@dataclass
class SemanticAnalysisResult:
    """Results from semantic similarity analysis."""
    score: float  # -1.0 (vulnerable) to +1.0 (resistant)
    confidence: float  # 0.0 to 1.0
    direct_similarity: float  # Similarity to injection prompt
    safe_similarity: float  # Similarity to safe baselines
    unsafe_similarity: float  # Similarity to unsafe baselines
    outcome: EvaluationOutcome
    reasoning: str


@dataclass
class StructuralPatternMatch:
    """A matched structural pattern."""
    pattern_name: str
    matches: List[str]
    score: float  # Positive = resistant, Negative = vulnerable
    confidence: float
    position_weight: float
    match_count: int


@dataclass
class StructuralAnalysisResult:
    """Results from structural pattern analysis."""
    patterns: List[StructuralPatternMatch]
    outcome: EvaluationOutcome
    confidence: float
    reasoning: str


@dataclass
class SignalResult:
    """Result from a single signal analyzer."""
    signal_type: str
    outcome: EvaluationOutcome
    score: float  # Normalized -1.0 to +1.0
    confidence: float
    metadata: Dict[str, any]
    reasoning: str


@dataclass
class Layer1Result:
    """Combined results from Layer 1 evaluation."""
    semantic: SemanticAnalysisResult
    structural: StructuralAnalysisResult
    aggregated_confidence: float
    aggregated_outcome: EvaluationOutcome
    signal_agreement: float  # 0.0 to 1.0


@dataclass
class EvaluationContext:
    """Context information for evaluation."""
    injection_prompt: str
    model_response: str
    base_prompt: str
    sample_metadata: Dict[str, any]  # category, technique, severity, language, etc.
    response_time: float


@dataclass
class EvaluationResult:
    """Final evaluation result."""
    injection_successful: bool  # True if injection succeeded (model vulnerable)
    confidence_score: float  # 0.0 to 1.0
    outcome: EvaluationOutcome
    severity: SeverityLevel
    safety_score: float  # 0.0 to 1.0
    robustness_score: Optional[float]
    compliance_score: Optional[float]
    reasoning: str
    evaluation_layer: EvaluationLayer  # Which layer produced this result
    layer_results: Dict[str, any]  # Detailed results from each layer
    detected_patterns: List[str]
    recommendations: List[str]
    mitigation_strategies: List[str]
    false_positive_checked: bool
    signal_breakdown: Dict[str, any]


# Type aliases for clarity
Embedding = List[float]
SimilarityScore = float  # 0.0 to 1.0
ConfidenceScore = float  # 0.0 to 1.0
EvaluationScore = float  # -1.0 to +1.0 (vulnerable to resistant)

