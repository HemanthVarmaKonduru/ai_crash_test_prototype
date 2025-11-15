"""
Type definitions for adversarial attacks evaluation system.

This module provides all type hints and data structures used throughout
the adversarial attacks evaluation system to ensure type safety and code clarity.
"""
from typing import Dict, List, Optional, Tuple, Literal
from dataclasses import dataclass
from enum import Enum


class EvaluationOutcome(str, Enum):
    """Possible evaluation outcomes for adversarial attacks."""
    RESISTANT = "resistant"  # Model successfully maintained robustness
    VULNERABLE = "vulnerable"  # Model was vulnerable to adversarial attack
    UNCERTAIN = "uncertain"  # Cannot determine with confidence


class SeverityLevel(str, Enum):
    """Severity levels for adversarial attacks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EvaluationLayer(str, Enum):
    """Evaluation layers used in the multi-layer system."""
    LAYER1_SEMANTIC = "layer1_semantic"
    LAYER1_STRUCTURAL = "layer1_structural"
    LAYER3_LLM = "layer3_llm"
    ENSEMBLE = "ensemble"


@dataclass
class SemanticAnalysisResult:
    """Results from semantic similarity analysis."""
    score: float  # -1.0 (vulnerable) to +1.0 (resistant)
    confidence: float  # 0.0 to 1.0
    direct_similarity: float  # Similarity to adversarial prompt
    safe_similarity: float  # Similarity to safe/resistant baselines
    unsafe_similarity: float  # Similarity to vulnerable/compliant baselines
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
    """Context information for adversarial attacks evaluation."""
    adversarial_prompt: str  # The adversarial input
    model_response: str  # Model's response
    base_prompt: str  # Base/system prompt
    judge_question: Optional[str] = None  # Optional judge question from dataset
    sample_metadata: Optional[Dict[str, any]] = None  # category, technique, risk_category, language, etc.
    response_time: float = 0.0


@dataclass
class EvaluationResult:
    """Final evaluation result for adversarial attacks."""
    adversarial_impact: bool  # True if adversarial attack succeeded (model vulnerable)
    confidence_score: float  # 0.0 to 1.0
    outcome: EvaluationOutcome
    severity: SeverityLevel
    safety_score: float  # 0.0 to 1.0
    robustness_score: Optional[float] = None  # Model robustness against adversarial inputs
    reasoning: str = ""
    evaluation_layer: EvaluationLayer = EvaluationLayer.LAYER1_SEMANTIC
    layer_results: Optional[Dict[str, any]] = None
    detected_patterns: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    mitigation_strategies: Optional[List[str]] = None
    false_positive_checked: bool = False
    signal_breakdown: Optional[Dict[str, any]] = None
    
    def __post_init__(self):
        """Set defaults for optional fields."""
        if self.layer_results is None:
            self.layer_results = {}
        if self.detected_patterns is None:
            self.detected_patterns = []
        if self.recommendations is None:
            self.recommendations = []
        if self.mitigation_strategies is None:
            self.mitigation_strategies = []
        if self.signal_breakdown is None:
            self.signal_breakdown = {}


# Type aliases for clarity
Embedding = List[float]
SimilarityScore = float  # 0.0 to 1.0
ConfidenceScore = float  # 0.0 to 1.0
EvaluationScore = float  # -1.0 to +1.0 (vulnerable to resistant)

