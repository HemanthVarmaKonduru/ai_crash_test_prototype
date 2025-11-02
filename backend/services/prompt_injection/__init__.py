"""
Prompt Injection Module - Multi-layer evaluation system for robust prompt injection detection.

This module implements a comprehensive evaluation system following the EVALUATION_LAYER_DESIGN.md
specification, providing:
- Layer 1: Semantic and Structural Analysis (fast, cost-effective)
- Layer 2: Rule-based Deep Analysis
- Layer 3: LLM-based Evaluation (for complex cases)
- Ensemble: Multiple evaluators for critical cases
"""

__version__ = "1.0.0"

