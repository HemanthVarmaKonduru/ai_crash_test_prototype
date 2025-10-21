"""
Job Executor Service main application.

Handles test job execution, queuing, and real-time updates via WebSocket.
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum
import asyncio
import uuid
import time
import sys
import os

# Add libs to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../libs/common/src"))

try:
    from events import EventPublisher, EventType, WebSocketEvent
except ImportError:
    # Mock for testing
    class EventPublisher:
        async def publish_event(self, event_type, user_id, data):
            return True
    
    class EventType:
        MODEL_STATUS_UPDATE = "model_status_update"
    
    class WebSocketEvent:
        pass

app = FastAPI(
    title="Adversarial Sandbox Job Executor",
    description="Job execution service for test suite processing",
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

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TestSuite(str, Enum):
    SAFETY = "safety"
    BIAS = "bias"
    ROBUSTNESS = "robustness"
    ADVERSARIAL = "adversarial"

class JobRequest(BaseModel):
    test_suite: TestSuite
    model_id: str
    user_id: str = "demo-user-123"
    config: Dict[str, Any] = Field(default_factory=dict)

class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str
    created_at: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: float = 0.0
    current_test: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

# In-memory job storage (in production, use Redis or database)
jobs_storage: Dict[str, Dict[str, Any]] = {}
active_connections: List[WebSocket] = []

# Event publisher for real-time updates
event_publisher = EventPublisher()

@app.post("/jobs", response_model=JobResponse)
async def create_job(request: JobRequest):
    """Create a new test job."""
    try:
        job_id = str(uuid.uuid4())
        current_time = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Store job metadata
        job_data = {
            "job_id": job_id,
            "user_id": request.user_id,
            "test_suite": request.test_suite,
            "model_id": request.model_id,
            "status": JobStatus.PENDING,
            "progress": 0.0,
            "config": request.config,
            "created_at": current_time,
            "started_at": None,
            "completed_at": None,
            "results": None,
            "error": None
        }
        
        jobs_storage[job_id] = job_data
        
        # Publish job created event
        await event_publisher.publish_event(
            event_type=EventType.MODEL_STATUS_UPDATE,
            user_id=request.user_id,
            data={
                "job_id": job_id,
                "status": "created",
                "test_suite": request.test_suite,
                "model_id": request.model_id
            }
        )
        
        # Start job execution in background
        asyncio.create_task(execute_job(job_id))
        
        return JobResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
            message="Job created and queued for execution",
            created_at=current_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")

@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get job status and results."""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_storage[job_id]
    
    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        current_test=job.get("current_test"),
        results=job.get("results"),
        error=job.get("error"),
        started_at=job.get("started_at"),
        completed_at=job.get("completed_at")
    )

@app.get("/jobs")
async def list_jobs(user_id: str = "demo-user-123"):
    """List jobs for a user."""
    user_jobs = [
        job for job in jobs_storage.values() 
        if job["user_id"] == user_id
    ]
    
    return {
        "jobs": user_jobs,
        "total": len(user_jobs),
        "user_id": user_id
    }

@app.delete("/jobs/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a job."""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_storage[job_id]
    if job["status"] in [JobStatus.COMPLETED, JobStatus.FAILED]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed job")
    
    job["status"] = JobStatus.CANCELLED
    job["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Publish cancellation event
    await event_publisher.publish_event(
        event_type=EventType.MODEL_STATUS_UPDATE,
        user_id=job["user_id"],
        data={
            "job_id": job_id,
            "status": "cancelled"
        }
    )
    
    return {"message": f"Job {job_id} cancelled successfully"}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time job updates."""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def execute_job(job_id: str):
    """Execute a test job."""
    try:
        job = jobs_storage[job_id]
        job["status"] = JobStatus.RUNNING
        job["started_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Publish job started event
        await event_publisher.publish_event(
            event_type=EventType.MODEL_STATUS_UPDATE,
            user_id=job["user_id"],
            data={
                "job_id": job_id,
                "status": "running",
                "test_suite": job["test_suite"]
            }
        )
        
        # Simulate test execution based on test suite
        test_suite = job["test_suite"]
        total_tests = get_test_count(test_suite)
        
        for i in range(total_tests):
            if job["status"] == JobStatus.CANCELLED:
                break
                
            # Update progress
            job["progress"] = (i + 1) / total_tests * 100
            job["current_test"] = f"Test {i + 1}/{total_tests}"
            
            # Publish progress update
            await event_publisher.publish_event(
                event_type=EventType.MODEL_STATUS_UPDATE,
                user_id=job["user_id"],
                data={
                    "job_id": job_id,
                    "status": "running",
                    "progress": job["progress"],
                    "current_test": job["current_test"]
                }
            )
            
            # Simulate test execution time
            await asyncio.sleep(2)
        
        # Generate results
        job["results"] = generate_test_results(test_suite)
        job["status"] = JobStatus.COMPLETED
        job["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Publish completion event
        await event_publisher.publish_event(
            event_type=EventType.MODEL_STATUS_UPDATE,
            user_id=job["user_id"],
            data={
                "job_id": job_id,
                "status": "completed",
                "results": job["results"]
            }
        )
        
    except Exception as e:
        job["status"] = JobStatus.FAILED
        job["error"] = str(e)
        job["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Publish error event
        await event_publisher.publish_event(
            event_type=EventType.MODEL_STATUS_UPDATE,
            user_id=job["user_id"],
            data={
                "job_id": job_id,
                "status": "failed",
                "error": str(e)
            }
        )

def get_test_count(test_suite: TestSuite) -> int:
    """Get number of tests for a test suite."""
    test_counts = {
        TestSuite.SAFETY: 5,
        TestSuite.BIAS: 4,
        TestSuite.ROBUSTNESS: 6,
        TestSuite.ADVERSARIAL: 8
    }
    return test_counts.get(test_suite, 3)

def generate_test_results(test_suite: TestSuite) -> Dict[str, Any]:
    """Generate mock test results."""
    import random
    
    base_results = {
        "test_suite": test_suite,
        "total_tests": get_test_count(test_suite),
        "passed_tests": 0,
        "failed_tests": 0,
        "overall_score": 0.0,
        "severity_breakdown": {
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0
        },
        "test_details": []
    }
    
    total_tests = get_test_count(test_suite)
    passed = random.randint(0, total_tests)
    failed = total_tests - passed
    
    base_results["passed_tests"] = passed
    base_results["failed_tests"] = failed
    base_results["overall_score"] = (passed / total_tests) * 100
    
    # Generate severity breakdown
    for _ in range(failed):
        severity = random.choice(["low", "medium", "high", "critical"])
        base_results["severity_breakdown"][severity] += 1
    
    return base_results

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "job-executor",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "active_jobs": len([j for j in jobs_storage.values() if j["status"] == JobStatus.RUNNING]),
        "total_jobs": len(jobs_storage)
    }
