"""
Unit tests for job management functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from main import app, JobStatus, TestSuite, JobRequest, JobResponse

class TestJobManagement:
    """Test job management operations."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.client = TestClient(app)
        self.sample_job_request = {
            "test_suite": "safety",
            "model_id": "demo-user-123:openai:gpt-3.5-turbo",
            "user_id": "demo-user-123",
            "config": {"temperature": 0.7}
        }
    
    def test_create_job_success(self):
        """Test successful job creation."""
        response = self.client.post("/jobs", json=self.sample_job_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert "job_id" in data
        assert "created_at" in data
        assert "Job created and queued for execution" in data["message"]
    
    def test_create_job_invalid_test_suite(self):
        """Test job creation with invalid test suite."""
        invalid_request = self.sample_job_request.copy()
        invalid_request["test_suite"] = "invalid_suite"
        
        response = self.client.post("/jobs", json=invalid_request)
        
        assert response.status_code == 422  # Validation error
    
    def test_get_job_status_success(self):
        """Test getting job status."""
        # First create a job
        create_response = self.client.post("/jobs", json=self.sample_job_request)
        job_id = create_response.json()["job_id"]
        
        # Then get job status
        response = self.client.get(f"/jobs/{job_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert data["status"] in ["pending", "running", "completed", "failed"]
    
    def test_get_job_status_not_found(self):
        """Test getting status for non-existent job."""
        response = self.client.get("/jobs/non-existent-job-id")
        
        assert response.status_code == 404
        assert "Job not found" in response.json()["detail"]
    
    def test_list_jobs_success(self):
        """Test listing jobs for a user."""
        # Create a job first
        self.client.post("/jobs", json=self.sample_job_request)
        
        # List jobs
        response = self.client.get("/jobs?user_id=demo-user-123")
        
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert "total" in data
        assert "user_id" in data
        assert data["user_id"] == "demo-user-123"
    
    def test_cancel_job_success(self):
        """Test cancelling a job."""
        # Create a job
        create_response = self.client.post("/jobs", json=self.sample_job_request)
        job_id = create_response.json()["job_id"]
        
        # Cancel the job
        response = self.client.delete(f"/jobs/{job_id}")
        
        assert response.status_code == 200
        assert f"Job {job_id} cancelled successfully" in response.json()["message"]
    
    def test_cancel_completed_job(self):
        """Test cancelling a completed job."""
        # This would require mocking a completed job
        with patch('main.jobs_storage') as mock_storage:
            mock_storage.__contains__ = Mock(return_value=True)
            mock_storage.__getitem__ = Mock(return_value={"status": "completed"})
            
            response = self.client.delete("/jobs/test-job-id")
            
            assert response.status_code == 400
            assert "Cannot cancel completed job" in response.json()["detail"]
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "job-executor"
        assert "timestamp" in data
        assert "active_jobs" in data
        assert "total_jobs" in data
    
    @pytest.mark.asyncio
    async def test_job_execution_simulation(self):
        """Test job execution simulation."""
        from main import execute_job, jobs_storage
        
        # Create a test job
        job_id = "test-job-123"
        jobs_storage[job_id] = {
            "job_id": job_id,
            "user_id": "demo-user-123",
            "test_suite": "safety",
            "status": "pending",
            "progress": 0.0,
            "config": {}
        }
        
        # Execute the job
        await execute_job(job_id)
        
        # Verify job was updated
        job = jobs_storage[job_id]
        assert job["status"] in ["completed", "failed"]
        assert job["progress"] == 100.0
        assert "started_at" in job
        assert "completed_at" in job
    
    def test_test_suite_enum_values(self):
        """Test test suite enum values."""
        assert TestSuite.SAFETY == "safety"
        assert TestSuite.BIAS == "bias"
        assert TestSuite.ROBUSTNESS == "robustness"
        assert TestSuite.ADVERSARIAL == "adversarial"
    
    def test_job_status_enum_values(self):
        """Test job status enum values."""
        assert JobStatus.PENDING == "pending"
        assert JobStatus.RUNNING == "running"
        assert JobStatus.COMPLETED == "completed"
        assert JobStatus.FAILED == "failed"
        assert JobStatus.CANCELLED == "cancelled"
    
    def test_job_request_validation(self):
        """Test job request validation."""
        # Valid request
        valid_request = JobRequest(
            test_suite=TestSuite.SAFETY,
            model_id="test-model",
            user_id="test-user"
        )
        assert valid_request.test_suite == TestSuite.SAFETY
        assert valid_request.model_id == "test-model"
        assert valid_request.user_id == "test-user"
    
    def test_job_response_creation(self):
        """Test job response creation."""
        response = JobResponse(
            job_id="test-job-123",
            status=JobStatus.PENDING,
            message="Test message",
            created_at="2025-01-18T10:00:00Z"
        )
        
        assert response.job_id == "test-job-123"
        assert response.status == JobStatus.PENDING
        assert response.message == "Test message"
        assert response.created_at == "2025-01-18T10:00:00Z"

