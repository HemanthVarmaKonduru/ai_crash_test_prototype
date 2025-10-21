"""
Unit tests for results aggregation functionality.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from main import app, TestSuite, SeverityLevel

class TestResultsAggregation:
    """Test results aggregation operations."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.client = TestClient(app)
        self.sample_model_id = "demo-user-123:openai:gpt-3.5-turbo"
        self.sample_user_id = "demo-user-123"
    
    def test_get_results_success(self):
        """Test successful results retrieval."""
        response = self.client.get(f"/results/{self.sample_model_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "model_id" in data
        assert "test_suite" in data
        assert "overall_score" in data
        assert "total_tests" in data
        assert "passed_tests" in data
        assert "failed_tests" in data
        assert "severity_breakdown" in data
        assert "risk_level" in data
        assert "recommendations" in data
        assert "timestamp" in data
        assert "test_details" in data
    
    def test_get_results_with_test_suite_filter(self):
        """Test results retrieval with test suite filter."""
        response = self.client.get(f"/results/{self.sample_model_id}?test_suite=safety")
        
        assert response.status_code == 200
        data = response.json()
        assert data["test_suite"] == "safety"
    
    def test_get_results_invalid_model_id(self):
        """Test results retrieval with invalid model ID."""
        response = self.client.get("/results/invalid-model-id")
        
        # Should still return mock results for demonstration
        assert response.status_code == 200
        data = response.json()
        assert data["model_id"] == "invalid-model-id"
    
    def test_get_metrics_success(self):
        """Test successful metrics retrieval."""
        response = self.client.get(f"/metrics/{self.sample_model_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "model_id" in data
        assert "metrics" in data
        assert "trends" in data
        assert "comparisons" in data
        assert "insights" in data
    
    def test_get_metrics_with_time_range(self):
        """Test metrics retrieval with time range filter."""
        response = self.client.get(f"/metrics/{self.sample_model_id}?time_range=7d")
        
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
        assert "trends" in data
    
    def test_get_insights_success(self):
        """Test successful insights retrieval."""
        response = self.client.get(f"/insights/{self.sample_model_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "model_id" in data
        assert "key_findings" in data
        assert "risk_assessment" in data
        assert "recommendations" in data
        assert "trends" in data
        assert "benchmark_comparison" in data
    
    def test_get_dashboard_data_success(self):
        """Test successful dashboard data retrieval."""
        response = self.client.get(f"/dashboard/{self.sample_user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "total_models" in data
        assert "total_tests" in data
        assert "average_score" in data
        assert "risk_distribution" in data
        assert "recent_activity" in data
        assert "top_risks" in data
        assert "performance_trends" in data
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "results-insights"
        assert "timestamp" in data
        assert "stored_results" in data
    
    def test_test_suite_enum_values(self):
        """Test test suite enum values."""
        assert TestSuite.SAFETY == "safety"
        assert TestSuite.BIAS == "bias"
        assert TestSuite.ROBUSTNESS == "robustness"
        assert TestSuite.ADVERSARIAL == "adversarial"
    
    def test_severity_level_enum_values(self):
        """Test severity level enum values."""
        assert SeverityLevel.LOW == "low"
        assert SeverityLevel.MEDIUM == "medium"
        assert SeverityLevel.HIGH == "high"
        assert SeverityLevel.CRITICAL == "critical"
    
    def test_results_response_structure(self):
        """Test results response structure."""
        from main import ResultsResponse
        
        response = ResultsResponse(
            user_id="test-user",
            model_id="test-model",
            test_suite=TestSuite.SAFETY,
            overall_score=85.5,
            total_tests=10,
            passed_tests=8,
            failed_tests=2,
            severity_breakdown={"low": 1, "medium": 1, "high": 0, "critical": 0},
            risk_level="medium",
            recommendations=["Test recommendation"],
            timestamp="2025-01-18T10:00:00Z",
            test_details=[]
        )
        
        assert response.user_id == "test-user"
        assert response.model_id == "test-model"
        assert response.test_suite == TestSuite.SAFETY
        assert response.overall_score == 85.5
        assert response.total_tests == 10
        assert response.passed_tests == 8
        assert response.failed_tests == 2
        assert response.risk_level == "medium"
    
    def test_metrics_response_structure(self):
        """Test metrics response structure."""
        from main import MetricsResponse
        
        response = MetricsResponse(
            user_id="test-user",
            model_id="test-model",
            metrics={"overall_score": 85.5},
            trends={"overall_score": []},
            comparisons={"industry_average": 75.0},
            insights=["Test insight"]
        )
        
        assert response.user_id == "test-user"
        assert response.model_id == "test-model"
        assert "overall_score" in response.metrics
        assert "overall_score" in response.trends
        assert "industry_average" in response.comparisons
        assert len(response.insights) == 1
    
    def test_insights_response_structure(self):
        """Test insights response structure."""
        from main import InsightsResponse
        
        response = InsightsResponse(
            user_id="test-user",
            model_id="test-model",
            key_findings=["Test finding"],
            risk_assessment={"overall_risk": "medium"},
            recommendations=["Test recommendation"],
            trends={"performance_trend": "improving"},
            benchmark_comparison={"vs_industry": "above_average"}
        )
        
        assert response.user_id == "test-user"
        assert response.model_id == "test-model"
        assert len(response.key_findings) == 1
        assert "overall_risk" in response.risk_assessment
        assert len(response.recommendations) == 1
        assert "performance_trend" in response.trends
        assert "vs_industry" in response.benchmark_comparison

