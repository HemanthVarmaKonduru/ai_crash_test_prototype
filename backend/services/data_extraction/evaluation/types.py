"""
Type definitions for data extraction evaluation system.

This module provides all type hints and data structures used throughout
the data extraction evaluation system to ensure type safety and code clarity.
"""
from typing import Dict, List, Optional, Tuple, Literal
from dataclasses import dataclass
from enum import Enum


class EvaluationOutcome(str, Enum):
    """Possible evaluation outcomes for data extraction attempts."""
    RESISTANT = "resistant"  # Model successfully resisted data extraction
    VULNERABLE = "vulnerable"  # Model leaked data (extraction successful)
    UNCERTAIN = "uncertain"  # Cannot determine with confidence


class SeverityLevel(str, Enum):
    """Severity levels for data extraction attempts."""
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
    score: float  # -1.0 (vulnerable/extracted) to +1.0 (resistant)
    confidence: float  # 0.0 to 1.0
    direct_similarity: float  # Similarity to extraction prompt
    base_similarity: float  # Similarity to base prompt (potential leakage)
    safe_similarity: float  # Similarity to safe/resistant baselines
    unsafe_similarity: float  # Similarity to vulnerable/leakage baselines
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
class DataLeakageResult:
    """Results from data leakage detection."""
    leakage_detected: bool
    leaked_values: List[str]
    sensitive_values_found: List[str]
    confidence: float
    outcome: EvaluationOutcome
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
    data_leakage: DataLeakageResult
    aggregated_confidence: float
    aggregated_outcome: EvaluationOutcome
    signal_agreement: float  # 0.0 to 1.0


@dataclass
class EvaluationContext:
    """Context information for data extraction evaluation."""
    base_prompt: str  # The system prompt containing potentially sensitive data
    extraction_prompt: str  # The user prompt attempting to extract data
    model_response: str  # The model's response
    judge_question: Optional[str]  # The question used to judge the response
    sample_metadata: Dict[str, any]  # category, technique, risk_category, language, etc.
    response_time: float


@dataclass
class EvaluationResult:
    """Final data extraction evaluation result."""
    data_extraction_successful: bool  # True if data was extracted (model vulnerable)
    confidence_score: float  # 0.0 to 1.0
    outcome: EvaluationOutcome
    severity: SeverityLevel
    safety_score: float  # 0.0 to 1.0
    robustness_score: Optional[float]
    privacy_score: Optional[float]  # Data protection effectiveness
    reasoning: str
    evaluation_layer: EvaluationLayer  # Which layer produced this result
    layer_results: Dict[str, any]  # Detailed results from each layer
    detected_patterns: List[str]
    leaked_data: List[str]  # Actual data that was extracted
    recommendations: List[str]
    mitigation_strategies: List[str]
    false_positive_checked: bool
    signal_breakdown: Dict[str, any]


# Type aliases for clarity
Embedding = List[float]
SimilarityScore = float  # 0.0 to 1.0
ConfidenceScore = float  # 0.0 to 1.0
EvaluationScore = float  # -1.0 to +1.0 (vulnerable to resistant)

