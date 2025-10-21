"""
Results & Insights Service

Handles test results aggregation, metrics calculation, and insights generation.
"""

from .main import app
from .metrics_calculator import MetricsCalculator
from .insights_generator import InsightsGenerator

__all__ = ["app", "MetricsCalculator", "InsightsGenerator"]

