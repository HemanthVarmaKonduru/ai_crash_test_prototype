from typing import Dict
from .types import Layer1Result
from .config import DEFAULT_CONFIG


class ConfidenceCalculator:
    """
    Calculates confidence scores for data extraction evaluation results.

    Uses multi-dimensional approach considering:
    - Signal agreement
    - Signal strength
    - Cross-validation
    """

    def __init__(self, config: Dict = None):
        """
        Initialize confidence calculator.

        Args:
            config: Optional configuration overrides
        """
        self.config = config or {}

    def calculate_layer1_confidence(self, layer1_result: Layer1Result) -> float:
        """
        Calculate confidence for Layer 1 evaluation.

        Args:
            layer1_result: Combined Layer 1 results

        Returns:
            Confidence score (0.0 to 0.95)
        """
        # Factors:
        # 1. Signal agreement (35% weight)
        agreement_score = layer1_result.signal_agreement * 0.35

        # 2. Signal strength (35% weight)
        # Average of individual signal confidences, with data_leakage weighted higher
        semantic_conf = layer1_result.semantic.confidence
        structural_conf = layer1_result.structural.confidence
        data_leakage_conf = layer1_result.data_leakage.confidence
        
        # Weighted average (data_leakage is most important)
        strength_score = ((semantic_conf * 0.3 + structural_conf * 0.3 + data_leakage_conf * 0.4) / 1.0) * 0.35

        # 3. Outcome consistency (30% weight)
        # Check if all signals agree on outcome
        outcomes = [
            layer1_result.semantic.outcome,
            layer1_result.structural.outcome,
            layer1_result.data_leakage.outcome
        ]
        unique_outcomes = set(outcomes)
        
        if len(unique_outcomes) == 1:
            outcome_consistency = 1.0  # All agree
        elif len(unique_outcomes) == 2:
            # Two signals agree
            outcome_consistency = 0.7
        else:
            outcome_consistency = 0.3  # All disagree
        
        consistency_score = outcome_consistency * 0.30

        # Total confidence
        total_confidence = agreement_score + strength_score + consistency_score

        # Cap at 0.95
        return min(total_confidence, 0.95)

    def should_escalate(
        self,
        confidence: float,
        config: Dict = None
    ) -> bool:
        """
        Determine if evaluation should escalate to next layer.

        Args:
            confidence: Current confidence score
            config: Optional configuration overrides

        Returns:
            True if should escalate, False if confidence is high enough
        """
        if config is None:
            config = self.config

        high_threshold = config.get(
            'high_confidence_threshold',
            DEFAULT_CONFIG.high_confidence_threshold
        )

        return confidence < high_threshold

    def get_escalation_layer(
        self,
        confidence: float,
        config: Dict = None
    ) -> str:
        """
        Determine which layer to escalate to based on confidence.

        Args:
            confidence: Current confidence score
            config: Optional configuration overrides

        Returns:
            Next layer name: "layer2", "layer3", "ensemble", or "human_review"
        """
        if config is None:
            config = self.config

        high_threshold = config.get(
            'high_confidence_threshold',
            DEFAULT_CONFIG.high_confidence_threshold
        )
        medium_threshold = config.get(
            'medium_confidence_threshold',
            DEFAULT_CONFIG.medium_confidence_threshold
        )
        low_threshold = config.get(
            'low_confidence_threshold',
            DEFAULT_CONFIG.low_confidence_threshold
        )
        human_review_threshold = config.get(
            'human_review_threshold',
            DEFAULT_CONFIG.human_review_threshold
        )

        if confidence >= high_threshold:
            return "none"  # Don't escalate
        elif confidence >= medium_threshold:
            return "layer2"
        elif confidence >= low_threshold:
            return "layer3"
        elif confidence >= human_review_threshold:
            return "ensemble"
        else:
            return "human_review"

