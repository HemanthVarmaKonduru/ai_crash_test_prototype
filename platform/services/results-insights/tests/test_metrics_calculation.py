"""
Unit tests for metrics calculation functionality.
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from main import (
    calculate_risk_level, 
    generate_recommendations, 
    generate_mock_results,
    generate_mock_metrics,
    generate_mock_insights,
    generate_mock_dashboard
)

class TestMetricsCalculation:
    """Test metrics calculation operations."""
    
    def test_calculate_risk_level_low(self):
        """Test risk level calculation for low risk."""
        assert calculate_risk_level(95.0) == "low"
        assert calculate_risk_level(90.0) == "low"
        assert calculate_risk_level(100.0) == "low"
    
    def test_calculate_risk_level_medium(self):
        """Test risk level calculation for medium risk."""
        assert calculate_risk_level(85.0) == "medium"
        assert calculate_risk_level(70.0) == "medium"
        assert calculate_risk_level(89.9) == "medium"
    
    def test_calculate_risk_level_high(self):
        """Test risk level calculation for high risk."""
        assert calculate_risk_level(65.0) == "high"
        assert calculate_risk_level(50.0) == "high"
        assert calculate_risk_level(69.9) == "high"
    
    def test_calculate_risk_level_critical(self):
        """Test risk level calculation for critical risk."""
        assert calculate_risk_level(45.0) == "critical"
        assert calculate_risk_level(30.0) == "critical"
        assert calculate_risk_level(0.0) == "critical"
        assert calculate_risk_level(49.9) == "critical"
    
    def test_generate_recommendations_low_score(self):
        """Test recommendation generation for low score."""
        result = {
            "overall_score": 60.0,
            "severity_breakdown": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "failed_tests": 2,
            "total_tests": 5
        }
        
        recommendations = generate_recommendations(result)
        
        assert len(recommendations) > 0
        assert any("retraining" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_critical_issues(self):
        """Test recommendation generation for critical issues."""
        result = {
            "overall_score": 80.0,
            "severity_breakdown": {"critical": 2, "high": 0, "medium": 0, "low": 0},
            "failed_tests": 2,
            "total_tests": 5
        }
        
        recommendations = generate_recommendations(result)
        
        assert len(recommendations) > 0
        assert any("critical" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_high_issues(self):
        """Test recommendation generation for high severity issues."""
        result = {
            "overall_score": 80.0,
            "severity_breakdown": {"critical": 0, "high": 3, "medium": 0, "low": 0},
            "failed_tests": 3,
            "total_tests": 5
        }
        
        recommendations = generate_recommendations(result)
        
        assert len(recommendations) > 0
        assert any("robustness" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_high_failure_rate(self):
        """Test recommendation generation for high failure rate."""
        result = {
            "overall_score": 80.0,
            "severity_breakdown": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "failed_tests": 4,
            "total_tests": 5
        }
        
        recommendations = generate_recommendations(result)
        
        assert len(recommendations) > 0
        assert any("comprehensive" in rec.lower() for rec in recommendations)
    
    def test_generate_mock_results_structure(self):
        """Test mock results generation structure."""
        from main import TestSuite
        
        result = generate_mock_results("test-model", TestSuite.SAFETY)
        
        assert "model_id" in result
        assert "user_id" in result
        assert "test_suite" in result
        assert "overall_score" in result
        assert "total_tests" in result
        assert "passed_tests" in result
        assert "failed_tests" in result
        assert "severity_breakdown" in result
        assert "timestamp" in result
        assert "test_details" in result
        
        assert result["model_id"] == "test-model"
        assert result["user_id"] == "demo-user-123"
        assert result["test_suite"] == TestSuite.SAFETY
        assert 0 <= result["overall_score"] <= 100
        assert result["total_tests"] == 5  # Safety test suite has 5 tests
        assert result["passed_tests"] + result["failed_tests"] == result["total_tests"]
    
    def test_generate_mock_metrics_structure(self):
        """Test mock metrics generation structure."""
        metrics = generate_mock_metrics("test-model")
        
        assert metrics.user_id == "demo-user-123"
        assert metrics.model_id == "test-model"
        assert "overall_score" in metrics.metrics
        assert "overall_score" in metrics.trends
        assert "industry_average" in metrics.comparisons
        assert len(metrics.insights) > 0
    
    def test_generate_mock_insights_structure(self):
        """Test mock insights generation structure."""
        insights = generate_mock_insights("test-model")
        
        assert insights.user_id == "demo-user-123"
        assert insights.model_id == "test-model"
        assert len(insights.key_findings) > 0
        assert "overall_risk" in insights.risk_assessment
        assert len(insights.recommendations) > 0
        assert "performance_trend" in insights.trends
        assert "vs_industry" in insights.benchmark_comparison
    
    def test_generate_mock_dashboard_structure(self):
        """Test mock dashboard generation structure."""
        dashboard = generate_mock_dashboard("test-user")
        
        assert "user_id" in dashboard
        assert "total_models" in dashboard
        assert "total_tests" in dashboard
        assert "average_score" in dashboard
        assert "risk_distribution" in dashboard
        assert "recent_activity" in dashboard
        assert "top_risks" in dashboard
        assert "performance_trends" in dashboard
        
        assert dashboard["user_id"] == "test-user"
        assert dashboard["total_models"] >= 0
        assert dashboard["total_tests"] >= 0
        assert 0 <= dashboard["average_score"] <= 100
        assert "low" in dashboard["risk_distribution"]
        assert "medium" in dashboard["risk_distribution"]
        assert "high" in dashboard["risk_distribution"]
        assert "critical" in dashboard["risk_distribution"]
        assert len(dashboard["recent_activity"]) >= 0
        assert len(dashboard["top_risks"]) >= 0
        assert "overall" in dashboard["performance_trends"]
    
    def test_mock_results_test_suite_variations(self):
        """Test mock results for different test suites."""
        from main import TestSuite
        
        # Test safety suite
        safety_result = generate_mock_results("test-model", TestSuite.SAFETY)
        assert safety_result["test_suite"] == TestSuite.SAFETY
        assert safety_result["total_tests"] == 5
        
        # Test bias suite
        bias_result = generate_mock_results("test-model", TestSuite.BIAS)
        assert bias_result["test_suite"] == TestSuite.BIAS
        assert bias_result["total_tests"] == 4
        
        # Test robustness suite
        robustness_result = generate_mock_results("test-model", TestSuite.ROBUSTNESS)
        assert robustness_result["test_suite"] == TestSuite.ROBUSTNESS
        assert robustness_result["total_tests"] == 6
        
        # Test adversarial suite
        adversarial_result = generate_mock_results("test-model", TestSuite.ADVERSARIAL)
        assert adversarial_result["test_suite"] == TestSuite.ADVERSARIAL
        assert adversarial_result["total_tests"] == 8
