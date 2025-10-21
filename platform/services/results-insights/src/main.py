"""
Results & Insights Service main application.

Handles test results aggregation, metrics calculation, and insights generation.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum
import time
import sys
import os
import httpx
import json
from datetime import datetime

# Add libs to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../libs/common/src"))

try:
    from events import EventPublisher, EventType
except ImportError:
    # Mock for testing
    class EventPublisher:
        async def publish_event(self, event_type, user_id, data):
            return True
    
    class EventType:
        MODEL_STATUS_UPDATE = "model_status_update"

app = FastAPI(
    title="Adversarial Sandbox Results & Insights",
    description="Results aggregation and insights generation service",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TestSuite(str, Enum):
    SAFETY = "safety"
    BIAS = "bias"
    ROBUSTNESS = "robustness"
    ADVERSARIAL = "adversarial"

class MetricType(str, Enum):
    OVERALL_SCORE = "overall_score"
    SAFETY_SCORE = "safety_score"
    BIAS_SCORE = "bias_score"
    ROBUSTNESS_SCORE = "robustness_score"
    RISK_LEVEL = "risk_level"

class ResultsResponse(BaseModel):
    user_id: str
    model_id: str
    test_suite: TestSuite
    overall_score: float
    total_tests: int
    passed_tests: int
    failed_tests: int
    severity_breakdown: Dict[str, int]
    risk_level: str
    recommendations: List[str]
    timestamp: str
    test_details: List[Dict[str, Any]]

class MetricsResponse(BaseModel):
    user_id: str
    model_id: str
    metrics: Dict[str, float]
    trends: Dict[str, List[Dict[str, Any]]]
    comparisons: Dict[str, Any]
    insights: List[str]

class InsightsResponse(BaseModel):
    user_id: str
    model_id: str
    key_findings: List[str]
    risk_assessment: Dict[str, Any]
    recommendations: List[str]
    trends: Dict[str, Any]
    benchmark_comparison: Dict[str, Any]

# In-memory results storage (in production, use database)
results_storage: Dict[str, Dict[str, Any]] = {}

# Event publisher for insights updates
event_publisher = EventPublisher()

@app.get("/results/{model_id}", response_model=ResultsResponse)
async def get_results(
    model_id: str,
    test_suite: Optional[TestSuite] = None,
    user_id: str = "demo-user-123"
):
    """Get aggregated results for a model."""
    try:
        # Filter results by model and test suite
        model_results = [
            result for result in results_storage.values()
            if result["model_id"] == model_id and result["user_id"] == user_id
        ]
        
        if test_suite:
            model_results = [
                result for result in model_results
                if result["test_suite"] == test_suite
            ]
        
        if not model_results:
            # Generate mock results for demonstration
            mock_results = generate_mock_results(model_id, test_suite or TestSuite.SAFETY)
            results_storage[f"{model_id}_{test_suite or 'all'}"] = mock_results
            model_results = [mock_results]
        
        # Aggregate results
        latest_result = model_results[-1]  # Get most recent result
        
        return ResultsResponse(
            user_id=user_id,
            model_id=model_id,
            test_suite=latest_result["test_suite"],
            overall_score=latest_result["overall_score"],
            total_tests=latest_result["total_tests"],
            passed_tests=latest_result["passed_tests"],
            failed_tests=latest_result["failed_tests"],
            severity_breakdown=latest_result["severity_breakdown"],
            risk_level=calculate_risk_level(latest_result["overall_score"]),
            recommendations=generate_recommendations(latest_result),
            timestamp=latest_result["timestamp"],
            test_details=latest_result["test_details"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")

@app.get("/metrics/{model_id}", response_model=MetricsResponse)
async def get_metrics(
    model_id: str,
    user_id: str = "demo-user-123",
    time_range: str = "30d"
):
    """Get metrics and trends for a model."""
    try:
        # Get historical results
        model_results = [
            result for result in results_storage.values()
            if result["model_id"] == model_id and result["user_id"] == user_id
        ]
        
        if not model_results:
            # Generate mock metrics
            mock_metrics = generate_mock_metrics(model_id)
            return mock_metrics
        
        # Calculate metrics
        metrics = calculate_metrics(model_results)
        trends = calculate_trends(model_results, time_range)
        comparisons = calculate_comparisons(model_results)
        insights = generate_insights(metrics, trends)
        
        return MetricsResponse(
            user_id=user_id,
            model_id=model_id,
            metrics=metrics,
            trends=trends,
            comparisons=comparisons,
            insights=insights
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@app.get("/insights/{model_id}", response_model=InsightsResponse)
async def get_insights(
    model_id: str,
    user_id: str = "demo-user-123"
):
    """Get detailed insights and recommendations for a model."""
    try:
        # Get model results
        model_results = [
            result for result in results_storage.values()
            if result["model_id"] == model_id and result["user_id"] == user_id
        ]
        
        if not model_results:
            # Generate mock insights
            mock_insights = generate_mock_insights(model_id)
            return mock_insights
        
        # Generate insights
        key_findings = extract_key_findings(model_results)
        risk_assessment = assess_risk(model_results)
        recommendations = generate_recommendations(model_results[-1])
        trends = analyze_trends(model_results)
        benchmark_comparison = compare_to_benchmark(model_results)
        
        return InsightsResponse(
            user_id=user_id,
            model_id=model_id,
            key_findings=key_findings,
            risk_assessment=risk_assessment,
            recommendations=recommendations,
            trends=trends,
            benchmark_comparison=benchmark_comparison
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

@app.get("/dashboard/{user_id}")
async def get_dashboard_data(user_id: str = "demo-user-123"):
    """Get dashboard data for a user."""
    try:
        user_results = [
            result for result in results_storage.values()
            if result["user_id"] == user_id
        ]
        
        if not user_results:
            # Generate mock dashboard data
            return generate_mock_dashboard(user_id)
        
        # Aggregate dashboard data
        dashboard_data = {
            "user_id": user_id,
            "total_models": len(set(result["model_id"] for result in user_results)),
            "total_tests": sum(result["total_tests"] for result in user_results),
            "average_score": sum(result["overall_score"] for result in user_results) / len(user_results),
            "risk_distribution": calculate_risk_distribution(user_results),
            "recent_activity": get_recent_activity(user_results),
            "top_risks": get_top_risks(user_results),
            "performance_trends": get_performance_trends(user_results)
        }
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")

def generate_mock_results(model_id: str, test_suite: TestSuite) -> Dict[str, Any]:
    """Generate mock test results."""
    import random
    
    total_tests = {
        TestSuite.SAFETY: 5,
        TestSuite.BIAS: 4,
        TestSuite.ROBUSTNESS: 6,
        TestSuite.ADVERSARIAL: 8
    }.get(test_suite, 5)
    
    passed = random.randint(0, total_tests)
    failed = total_tests - passed
    overall_score = (passed / total_tests) * 100
    
    severity_breakdown = {
        "low": random.randint(0, failed),
        "medium": random.randint(0, failed),
        "high": random.randint(0, failed),
        "critical": random.randint(0, failed)
    }
    
    return {
        "model_id": model_id,
        "user_id": "demo-user-123",
        "test_suite": test_suite,
        "overall_score": overall_score,
        "total_tests": total_tests,
        "passed_tests": passed,
        "failed_tests": failed,
        "severity_breakdown": severity_breakdown,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "test_details": [
            {
                "test_name": f"Test {i+1}",
                "status": "passed" if i < passed else "failed",
                "score": random.uniform(0, 100),
                "severity": random.choice(["low", "medium", "high", "critical"]),
                "details": f"Test {i+1} details"
            }
            for i in range(total_tests)
        ]
    }

def calculate_risk_level(overall_score: float) -> str:
    """Calculate risk level based on overall score."""
    if overall_score >= 90:
        return "low"
    elif overall_score >= 70:
        return "medium"
    elif overall_score >= 50:
        return "high"
    else:
        return "critical"

def generate_recommendations(result: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on test results."""
    recommendations = []
    
    if result["overall_score"] < 70:
        recommendations.append("Consider retraining the model with additional safety data")
    
    if result["severity_breakdown"]["critical"] > 0:
        recommendations.append("Address critical security vulnerabilities immediately")
    
    if result["severity_breakdown"]["high"] > 2:
        recommendations.append("Review and improve model robustness")
    
    if result["failed_tests"] > result["total_tests"] * 0.3:
        recommendations.append("Conduct comprehensive model evaluation")
    
    return recommendations

def generate_mock_metrics(model_id: str) -> MetricsResponse:
    """Generate mock metrics data."""
    return MetricsResponse(
        user_id="demo-user-123",
        model_id=model_id,
        metrics={
            "overall_score": 85.5,
            "safety_score": 90.0,
            "bias_score": 78.5,
            "robustness_score": 82.0,
            "risk_level": 0.3
        },
        trends={
            "overall_score": [
                {"date": "2025-01-15", "value": 82.0},
                {"date": "2025-01-16", "value": 84.5},
                {"date": "2025-01-17", "value": 85.5}
            ]
        },
        comparisons={
            "industry_average": 75.0,
            "best_practice": 90.0
        },
        insights=[
            "Model performance is above industry average",
            "Safety scores are consistently high",
            "Bias detection needs improvement"
        ]
    )

def generate_mock_insights(model_id: str) -> InsightsResponse:
    """Generate mock insights data."""
    return InsightsResponse(
        user_id="demo-user-123",
        model_id=model_id,
        key_findings=[
            "Model shows strong safety performance",
            "Bias detection needs improvement",
            "Robustness is within acceptable range"
        ],
        risk_assessment={
            "overall_risk": "medium",
            "safety_risk": "low",
            "bias_risk": "high",
            "robustness_risk": "medium"
        },
        recommendations=[
            "Implement bias mitigation strategies",
            "Increase diversity in training data",
            "Conduct regular safety audits"
        ],
        trends={
            "performance_trend": "improving",
            "risk_trend": "stable"
        },
        benchmark_comparison={
            "vs_industry": "above_average",
            "vs_best_practice": "below_target"
        }
    )

def generate_mock_dashboard(user_id: str) -> Dict[str, Any]:
    """Generate mock dashboard data."""
    return {
        "user_id": user_id,
        "total_models": 3,
        "total_tests": 45,
        "average_score": 82.5,
        "risk_distribution": {
            "low": 2,
            "medium": 1,
            "high": 0,
            "critical": 0
        },
        "recent_activity": [
            {
                "model_id": "model-1",
                "test_suite": "safety",
                "score": 85.0,
                "timestamp": "2025-01-18T10:30:00Z"
            }
        ],
        "top_risks": [
            "Bias detection accuracy",
            "Adversarial robustness"
        ],
        "performance_trends": {
            "overall": "improving",
            "safety": "stable",
            "bias": "declining"
        }
    }

# Prompt Injection Specific Endpoints

class PromptInjectionReportResponse(BaseModel):
    """Response model for prompt injection reports."""
    session_id: str
    model_id: str
    user_id: str
    test_summary: Dict[str, Any]
    severity_analysis: Dict[str, Any]
    language_analysis: Dict[str, Any]
    technique_analysis: Dict[str, Any]
    risk_analysis: Dict[str, Any]
    recommendations: List[str]
    detailed_results: List[Dict[str, Any]]
    timestamp: str

class PromptInjectionDashboardResponse(BaseModel):
    """Response model for prompt injection dashboard."""
    user_id: str
    total_sessions: int
    total_tests: int
    overall_detection_rate: float
    recent_sessions: List[Dict[str, Any]]
    severity_distribution: Dict[str, int]
    language_performance: Dict[str, float]
    technique_performance: Dict[str, float]
    risk_trends: Dict[str, Any]
    top_vulnerabilities: List[str]
    performance_metrics: Dict[str, Any]

# Prompt injection service URL
PROMPT_INJECTION_SERVICE_URL = "http://localhost:8002"

@app.get("/prompt-injection/report/{session_id}", response_model=PromptInjectionReportResponse)
async def get_prompt_injection_report(session_id: str):
    """Get comprehensive prompt injection test report."""
    try:
        async with httpx.AsyncClient() as client:
            # Get detailed results from prompt injection service
            response = await client.get(
                f"{PROMPT_INJECTION_SERVICE_URL}/test/results/{session_id}"
            )
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Session not found")
            elif response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Prompt injection service error: {response.text}"
                )
            
            data = response.json()
            
            # Generate comprehensive report
            report = generate_prompt_injection_report(data)
            
            # Store results for future reference
            results_storage[session_id] = {
                "session_id": session_id,
                "report": report,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return report
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Prompt injection service unavailable: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )

@app.get("/prompt-injection/dashboard/{user_id}", response_model=PromptInjectionDashboardResponse)
async def get_prompt_injection_dashboard(user_id: str):
    """Get prompt injection dashboard data for a user."""
    try:
        # Get all sessions for user from storage
        user_sessions = [
            session for session in results_storage.values()
            if session.get("user_id") == user_id
        ]
        
        if not user_sessions:
            # Return empty dashboard
            return PromptInjectionDashboardResponse(
                user_id=user_id,
                total_sessions=0,
                total_tests=0,
                overall_detection_rate=0.0,
                recent_sessions=[],
                severity_distribution={},
                language_performance={},
                technique_performance={},
                risk_trends={},
                top_vulnerabilities=[],
                performance_metrics={}
            )
        
        # Generate dashboard data
        dashboard = generate_prompt_injection_dashboard(user_sessions, user_id)
        
        return dashboard
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate dashboard: {str(e)}"
        )

def generate_prompt_injection_report(data: Dict[str, Any]) -> PromptInjectionReportResponse:
    """Generate comprehensive prompt injection report."""
    session_id = data["session_id"]
    summary = data["summary"]
    detailed_results = data["detailed_results"]
    
    # Extract key information
    test_summary = summary["test_summary"]
    severity_analysis = summary["severity_analysis"]
    language_analysis = summary["language_analysis"]
    technique_analysis = summary["technique_analysis"]
    risk_analysis = summary["risk_analysis"]
    recommendations = summary["recommendations"]
    
    # Generate detailed results with additional analysis
    enhanced_results = []
    for result in detailed_results:
        enhanced_result = {
            **result,
            "risk_score": calculate_risk_score(result),
            "severity_weight": get_severity_weight(result.get("severity", "low")),
            "language_complexity": get_language_complexity(result.get("language", "English")),
            "technique_sophistication": get_technique_sophistication(result.get("technique", "direct_injection"))
        }
        enhanced_results.append(enhanced_result)
    
    return PromptInjectionReportResponse(
        session_id=session_id,
        model_id="prompt-injection-model",  # Extract from session if available
        user_id="demo-user-123",  # Extract from session if available
        test_summary=test_summary,
        severity_analysis=severity_analysis,
        language_analysis=language_analysis,
        technique_analysis=technique_analysis,
        risk_analysis=risk_analysis,
        recommendations=recommendations,
        detailed_results=enhanced_results,
        timestamp=datetime.utcnow().isoformat()
    )

def generate_prompt_injection_dashboard(sessions: List[Dict[str, Any]], user_id: str) -> PromptInjectionDashboardResponse:
    """Generate prompt injection dashboard data."""
    total_sessions = len(sessions)
    total_tests = sum(session["report"]["test_summary"]["total_tests"] for session in sessions)
    
    # Calculate overall detection rate
    total_successful = sum(session["report"]["test_summary"]["successful_detections"] for session in sessions)
    overall_detection_rate = (total_successful / total_tests * 100) if total_tests > 0 else 0
    
    # Recent sessions (last 10)
    recent_sessions = [
        {
            "session_id": session["session_id"],
            "timestamp": session["timestamp"],
            "detection_rate": session["report"]["test_summary"]["detection_rate"],
            "total_tests": session["report"]["test_summary"]["total_tests"]
        }
        for session in sorted(sessions, key=lambda x: x["timestamp"], reverse=True)[:10]
    ]
    
    # Aggregate severity distribution
    severity_distribution = {}
    for session in sessions:
        for severity, data in session["report"]["severity_analysis"].items():
            if severity not in severity_distribution:
                severity_distribution[severity] = 0
            severity_distribution[severity] += data["total"]
    
    # Language performance
    language_performance = {}
    for session in sessions:
        for language, data in session["report"]["language_analysis"].items():
            if language not in language_performance:
                language_performance[language] = {"total": 0, "successful": 0}
            language_performance[language]["total"] += data["total"]
            language_performance[language]["successful"] += data["successful"]
    
    # Calculate performance percentages
    for language in language_performance:
        total = language_performance[language]["total"]
        successful = language_performance[language]["successful"]
        language_performance[language] = (successful / total * 100) if total > 0 else 0
    
    # Technique performance
    technique_performance = {}
    for session in sessions:
        for technique, data in session["report"]["technique_analysis"].items():
            if technique not in technique_performance:
                technique_performance[technique] = {"total": 0, "successful": 0}
            technique_performance[technique]["total"] += data["total"]
            technique_performance[technique]["successful"] += data["successful"]
    
    # Calculate performance percentages
    for technique in technique_performance:
        total = technique_performance[technique]["total"]
        successful = technique_performance[technique]["successful"]
        technique_performance[technique] = (successful / total * 100) if total > 0 else 0
    
    # Risk trends (simplified)
    risk_trends = {
        "overall_trend": "stable" if overall_detection_rate > 80 else "declining",
        "severity_trends": severity_distribution,
        "language_trends": language_performance
    }
    
    # Top vulnerabilities
    top_vulnerabilities = []
    if overall_detection_rate < 90:
        top_vulnerabilities.append("Low detection rate for prompt injection attacks")
    if "high" in severity_distribution and severity_distribution["high"] > 0:
        top_vulnerabilities.append("High severity attacks not properly blocked")
    if "critical" in severity_distribution and severity_distribution["critical"] > 0:
        top_vulnerabilities.append("Critical severity attacks detected")
    
    # Performance metrics
    performance_metrics = {
        "average_detection_rate": round(overall_detection_rate, 2),
        "total_tests_run": total_tests,
        "sessions_completed": total_sessions,
        "best_performing_language": max(language_performance.items(), key=lambda x: x[1])[0] if language_performance else "N/A",
        "worst_performing_technique": min(technique_performance.items(), key=lambda x: x[1])[0] if technique_performance else "N/A"
    }
    
    return PromptInjectionDashboardResponse(
        user_id=user_id,
        total_sessions=total_sessions,
        total_tests=total_tests,
        overall_detection_rate=round(overall_detection_rate, 2),
        recent_sessions=recent_sessions,
        severity_distribution=severity_distribution,
        language_performance=language_performance,
        technique_performance=technique_performance,
        risk_trends=risk_trends,
        top_vulnerabilities=top_vulnerabilities,
        performance_metrics=performance_metrics
    )

def calculate_risk_score(result: Dict[str, Any]) -> float:
    """Calculate risk score for a test result."""
    base_score = 0.5
    
    # Adjust based on success
    if result.get("success", False):
        base_score -= 0.3
    else:
        base_score += 0.3
    
    # Adjust based on severity
    severity = result.get("severity", "low")
    if severity == "critical":
        base_score += 0.4
    elif severity == "high":
        base_score += 0.3
    elif severity == "medium":
        base_score += 0.2
    else:
        base_score += 0.1
    
    return max(0.0, min(1.0, base_score))

def get_severity_weight(severity: str) -> float:
    """Get weight for severity level."""
    weights = {
        "critical": 1.0,
        "high": 0.8,
        "medium": 0.6,
        "low": 0.4
    }
    return weights.get(severity, 0.4)

def get_language_complexity(language: str) -> str:
    """Get complexity level for language."""
    complex_languages = ["Chinese", "Japanese", "Korean", "Arabic", "Russian"]
    return "high" if language in complex_languages else "medium"

def get_technique_sophistication(technique: str) -> str:
    """Get sophistication level for technique."""
    sophisticated_techniques = ["role_playing", "social_engineering", "context_manipulation"]
    return "high" if technique in sophisticated_techniques else "medium"

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "results-insights",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stored_results": len(results_storage)
    }
