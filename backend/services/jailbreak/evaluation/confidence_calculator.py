"""
Confidence Calculator - Multi-dimensional confidence scoring for jailbreak detection.

This module calculates confidence scores based on multiple factors:
- Signal agreement
- Signal strength
- Cross-layer agreement
"""
from typing import Dict
from .types import Layer1Result
from .config import DEFAULT_CONFIG


class ConfidenceCalculator:
    """
    Calculates confidence scores for jailbreak evaluation results.
    
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
        # 1. Signal agreement (40% weight)
        agreement_score = layer1_result.signal_agreement * 0.4
        
        # 2. Signal strength (30% weight)
        # Average of individual signal confidences
        semantic_conf = layer1_result.semantic.confidence
        structural_conf = layer1_result.structural.confidence
        strength_score = ((semantic_conf + structural_conf) / 2) * 0.3
        
        # 3. Outcome consistency (30% weight)
        # If both signals agree on outcome, higher confidence
        outcome_consistency = 1.0 if (
            layer1_result.semantic.outcome == layer1_result.structural.outcome
        ) else 0.5
        consistency_score = outcome_consistency * 0.3
        
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
            Next layer name: "layer3", "ensemble", or "human_review"
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
            return "layer3"  # Skip layer2 for jailbreak
        elif confidence >= low_threshold:
            return "layer3"
        elif confidence >= human_review_threshold:
            return "ensemble"
        else:
            return "human_review"

