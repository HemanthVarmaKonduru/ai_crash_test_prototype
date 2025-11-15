"""
Main FastAPI application for Evalence Security Testing Platform.
"""
import sys
import os
import time
import uuid
from typing import Dict, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from backend.config.settings import (
    CORS_ORIGINS, MAX_PROMPTS_PI, MAX_PROMPTS_JB, MAX_PROMPTS_DE, MAX_PROMPTS_ADVERSARIAL,
    TARGET_MODEL, JUDGE_MODEL,
    OLLAMA_FIREWALL_MODEL, OLLAMA_API_KEY, OLLAMA_HOST, USE_OLLAMA_FOR_EVALUATION
)
from backend.models.schemas import (
    TestRequest, TestResponse, LoginRequest, LoginResponse,
    LogoutRequest, VerifyRequest, FirewallEvaluationRequest, FirewallEvaluationResponse,
    FirewallChatRequest, FirewallChatResponse
)
from backend.services.auth import (
    validate_credentials, create_session, delete_session,
    is_session_valid, get_session
)
from backend.services.test_executor import (
    execute_prompt_injection_test,
    execute_jailbreak_test,
    execute_data_extraction_test,
    execute_adversarial_attacks_test
)
from backend.services.analytics import AnalyticsService

# Global storage for test sessions
test_sessions: Dict[str, Dict[str, Any]] = {}

# Initialize FastAPI app
app = FastAPI(
    title="Evalence Security Testing API",
    description="API for comprehensive AI security testing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Health Check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "evalence-security-testing"}

# Authentication Endpoints
@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """User login endpoint with static credentials."""
    try:
        if validate_credentials(request.email, request.password):
            token = create_session(request.email)
            return LoginResponse(
                success=True,
                message="Login successful",
                token=token,
                user={
                    "email": request.email,
                    "token": token
                }
            )
        else:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(e)}"
        )

@app.post("/api/v1/auth/logout")
async def logout(request: LogoutRequest):
    """User logout endpoint."""
    try:
        if delete_session(request.token):
            return {"success": True, "message": "Logout successful"}
        else:
            raise HTTPException(status_code=401, detail="Invalid token")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Logout failed: {str(e)}"
        )

@app.post("/api/v1/auth/verify")
async def verify_token(request: VerifyRequest):
    """Verify if a token is valid."""
    try:
        if is_session_valid(request.token):
            session = get_session(request.token)
            return {
                "valid": True,
                "user": {
                    "email": session["email"]
                }
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Verification failed: {str(e)}"
        )

# Prompt Injection Endpoints
@app.post("/api/v1/test/prompt-injection/start", response_model=TestResponse)
async def start_prompt_injection_test(request: TestRequest, background_tasks: BackgroundTasks):
    """Start a prompt injection test run."""
    try:
        test_id = f"pi_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        
        test_sessions[test_id] = {
            "test_id": test_id,
            "status": "initializing",
            "progress": 0,
            "current_step": "Loading prompt injection dataset...",
            "total_tests": 0,
            "completed_tests": 0,
            "start_time": datetime.now().isoformat(),
            "results": {},
            "captured_responses": [],
            "evaluated_responses": [],
            "error": None
        }
        
        background_tasks.add_task(
            execute_prompt_injection_test,
            test_id,
            test_sessions[test_id]
        )
        
        return TestResponse(
            test_id=test_id,
            status="initializing",
            message="Prompt injection test started successfully",
            progress=0,
            current_step="Loading prompt injection dataset...",
            total_tests=MAX_PROMPTS_PI
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start prompt injection test: {str(e)}")

@app.get("/api/v1/test/prompt-injection/{test_id}/status", response_model=TestResponse)
async def get_prompt_injection_test_status(test_id: str):
    """Get the current status of a prompt injection test run."""
    if test_id not in test_sessions:
        raise HTTPException(status_code=404, detail="Prompt injection test not found")
    
    session = test_sessions[test_id]
    return TestResponse(
        test_id=test_id,
        status=session["status"],
        message=session.get("current_step", ""),
        progress=session["progress"],
        current_step=session.get("current_step", ""),
        total_tests=session["total_tests"],
        completed_tests=session["completed_tests"],
        results=session["results"]
    )

@app.get("/api/v1/test/prompt-injection/{test_id}/results")
async def get_prompt_injection_test_results(test_id: str):
    """Get the final results of a completed prompt injection test."""
    if test_id not in test_sessions:
        raise HTTPException(status_code=404, detail="Prompt injection test not found")
    
    session = test_sessions[test_id]
    if session["status"] != "completed":
        raise HTTPException(status_code=400, detail="Prompt injection test not completed yet")
    
    return {
        "test_id": test_id,
        "status": session["status"],
        "start_time": session["start_time"],
        "end_time": session.get("end_time"),
        "total_tests": session["total_tests"],
        "completed_tests": session["completed_tests"],
        "total_execution_time": session["results"].get("total_execution_time", 0),
        "detection_rate": session["results"].get("detection_rate", 0),
        "successful_resistances": session["results"].get("successful_resistances", 0),
        "failed_resistances": session["results"].get("failed_resistances", 0),
        "captured_responses": session["captured_responses"],
        "evaluated_responses": session["evaluated_responses"],
        "detailed_analysis": session["results"].get("detailed_analysis", {}),
        "performance_metrics": session["results"].get("performance_metrics", {})
    }

@app.get("/api/v1/test/prompt-injection/{test_id}/download")
async def download_prompt_injection_test_report(test_id: str):
    """Download the prompt injection test report as JSON."""
    if test_id not in test_sessions:
        raise HTTPException(status_code=404, detail="Prompt injection test not found")
    
    session = test_sessions[test_id]
    if session["status"] != "completed":
        raise HTTPException(status_code=400, detail="Prompt injection test not completed yet")
    
    report = {
        "test_metadata": {
            "test_id": test_id,
            "start_time": session["start_time"],
            "end_time": session.get("end_time"),
            "total_tests": session["total_tests"],
            "model_tested": TARGET_MODEL,
            "judge_model": JUDGE_MODEL,
            "api_key_used": "***masked***"
        },
        "summary": {
            "detection_rate": session["results"].get("detection_rate", 0),
            "successful_resistances": session["results"].get("successful_resistances", 0),
            "failed_resistances": session["results"].get("failed_resistances", 0),
            "total_execution_time": session["results"].get("total_execution_time", 0)
        },
        "detailed_results": session["evaluated_responses"],
        "performance_metrics": session["results"].get("performance_metrics", {}),
        "analysis": session["results"].get("detailed_analysis", {})
    }
    return report

# Jailbreak Endpoints
@app.post("/api/v1/test/jailbreak/start", response_model=TestResponse)
async def start_jailbreak_test(request: TestRequest, background_tasks: BackgroundTasks):
    """Start a jailbreak test run."""
    try:
        test_id = f"jb_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        
        test_sessions[test_id] = {
            "test_id": test_id,
            "status": "initializing",
            "progress": 0,
            "current_step": "Loading jailbreak dataset...",
            "total_tests": 0,
            "completed_tests": 0,
            "start_time": datetime.now().isoformat(),
            "results": {},
            "captured_responses": [],
            "evaluated_responses": [],
            "error": None
        }
        
        background_tasks.add_task(
            execute_jailbreak_test,
            test_id,
            test_sessions[test_id]
        )
        
        return TestResponse(
            test_id=test_id,
            status="initializing",
            message="Jailbreak test started successfully",
            progress=0,
            current_step="Loading jailbreak dataset...",
            total_tests=MAX_PROMPTS_JB
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start jailbreak test: {str(e)}")

@app.get("/api/v1/test/jailbreak/{test_id}/status", response_model=TestResponse)
async def get_jailbreak_test_status(test_id: str):
    """Get the current status of a jailbreak test run."""
    if test_id not in test_sessions:
        raise HTTPException(status_code=404, detail="Jailbreak test not found")
    
    session = test_sessions[test_id]
    return TestResponse(
        test_id=test_id,
        status=session["status"],
        message=session.get("current_step", ""),
        progress=session["progress"],
        current_step=session.get("current_step", ""),
        total_tests=session["total_tests"],
        completed_tests=session["completed_tests"],
        results=session["results"]
    )

@app.get("/api/v1/test/jailbreak/{test_id}/results")
async def get_jailbreak_test_results(test_id: str):
    """Get the final results of a completed jailbreak test."""
    if test_id not in test_sessions:
        raise HTTPException(status_code=404, detail="Jailbreak test not found")
    
    session = test_sessions[test_id]
    if session["status"] != "completed":
        raise HTTPException(status_code=400, detail="Jailbreak test not completed yet")
    
    return {
        "test_id": test_id,
        "status": session["status"],
        "start_time": session["start_time"],
        "end_time": session.get("end_time"),
        "total_tests": session["total_tests"],
        "completed_tests": session["completed_tests"],
        "detection_rate": session["results"].get("detection_rate", 0),
        "successful_resistances": session["results"].get("successful_resistances", 0),
        "failed_resistances": session["results"].get("failed_resistances", 0),
        "total_execution_time": session["results"].get("total_execution_time"),
        "captured_responses": session["captured_responses"],
        "evaluated_responses": session["evaluated_responses"],
        "detailed_analysis": session["results"].get("detailed_analysis", {}),
        "performance_metrics": session["results"].get("performance_metrics", {})
    }

@app.get("/api/v1/test/jailbreak/{test_id}/download")
async def download_jailbreak_test_report(test_id: str):
    """Download the jailbreak test report as JSON."""
    if test_id not in test_sessions:
        raise HTTPException(status_code=404, detail="Jailbreak test not found")
    
    session = test_sessions[test_id]
    if session["status"] != "completed":
        raise HTTPException(status_code=400, detail="Jailbreak test not completed yet")
    
    report = {
        "test_metadata": {
            "test_id": test_id,
            "start_time": session["start_time"],
            "end_time": session.get("end_time"),
            "total_tests": session["total_tests"],
            "model_tested": TARGET_MODEL,
            "judge_model": JUDGE_MODEL,
            "api_key_used": "***masked***"
        },
        "summary": {
            "detection_rate": session["results"].get("detection_rate", 0),
            "successful_resistances": session["results"].get("successful_resistances", 0),
            "failed_resistances": session["results"].get("failed_resistances", 0),
            "total_execution_time": session["results"].get("total_execution_time", 0)
        },
        "detailed_results": session["evaluated_responses"],
        "performance_metrics": session["results"].get("performance_metrics", {}),
        "analysis": session["results"].get("detailed_analysis", {})
    }
    return report

# Data Extraction Endpoints
@app.post("/api/v1/test/data-extraction/start", response_model=TestResponse)
async def start_data_extraction_test(request: TestRequest, background_tasks: BackgroundTasks):
    """Start a data extraction test run."""
    try:
        test_id = f"de_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        
        test_sessions[test_id] = {
            "test_id": test_id,
            "status": "initializing",
            "progress": 0,
            "current_step": "Loading data extraction dataset...",
            "total_tests": 0,
            "completed_tests": 0,
            "start_time": datetime.now().isoformat(),
            "results": {},
            "captured_responses": [],
            "evaluated_responses": [],
            "error": None
        }
        
        background_tasks.add_task(
            execute_data_extraction_test,
            test_id,
            test_sessions[test_id]
        )
        
        return TestResponse(
            test_id=test_id,
            status="initializing",
            message="Data extraction test started successfully",
            progress=0,
            current_step="Loading data extraction dataset...",
            total_tests=MAX_PROMPTS_DE
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start data extraction test: {str(e)}")

@app.get("/api/v1/test/data-extraction/{test_id}/status", response_model=TestResponse)
async def get_data_extraction_test_status(test_id: str):
    """Get the current status of a data extraction test run."""
    if test_id not in test_sessions:
        raise HTTPException(status_code=404, detail="Data extraction test not found")
    
    session = test_sessions[test_id]
    return TestResponse(
        test_id=test_id,
        status=session["status"],
        message=session.get("current_step", ""),
        progress=session["progress"],
        current_step=session.get("current_step", ""),
        total_tests=session["total_tests"],
        completed_tests=session["completed_tests"],
        results=session["results"]
    )

@app.get("/api/v1/test/data-extraction/{test_id}/results")
async def get_data_extraction_test_results(test_id: str):
    """Get the final results of a completed data extraction test."""
    if test_id not in test_sessions:
        raise HTTPException(status_code=404, detail="Data extraction test not found")
    
    session = test_sessions[test_id]
    if session["status"] != "completed":
        raise HTTPException(status_code=400, detail="Data extraction test not completed yet")
    
    return {
        "test_id": test_id,
        "status": session["status"],
        "start_time": session["start_time"],
        "end_time": session.get("end_time"),
        "total_tests": session["total_tests"],
        "completed_tests": session["completed_tests"],
        "detection_rate": session["results"].get("detection_rate", 0),
        "successful_resistances": session["results"].get("successful_resistances", 0),
        "failed_extractions": session["results"].get("failed_extractions", 0),
        "total_execution_time": session["results"].get("total_execution_time"),
        "captured_responses": session["captured_responses"],
        "evaluated_responses": session["evaluated_responses"],
        "detailed_analysis": session["results"].get("detailed_analysis", {}),
        "performance_metrics": session["results"].get("performance_metrics", {})
    }

@app.get("/api/v1/test/data-extraction/{test_id}/download")
async def download_data_extraction_test_report(test_id: str):
    """Download the data extraction test report as JSON."""
    if test_id not in test_sessions:
        raise HTTPException(status_code=404, detail="Data extraction test not found")
    
    session = test_sessions[test_id]
    if session["status"] != "completed":
        raise HTTPException(status_code=400, detail="Data extraction test not completed yet")
    
    report = {
        "test_metadata": {
            "test_id": test_id,
            "start_time": session["start_time"],
            "end_time": session.get("end_time"),
            "total_tests": session["total_tests"],
            "model_tested": TARGET_MODEL,
            "judge_model": JUDGE_MODEL,
            "api_key_used": "***masked***"
        },
        "summary": {
            "detection_rate": session["results"].get("detection_rate", 0),
            "successful_resistances": session["results"].get("successful_resistances", 0),
            "failed_extractions": session["results"].get("failed_extractions", 0),
            "total_execution_time": session["results"].get("total_execution_time", 0)
        },
        "detailed_results": session["evaluated_responses"],
        "performance_metrics": session["results"].get("performance_metrics", {}),
        "analysis": session["results"].get("detailed_analysis", {})
    }
    return report

# Adversarial Attacks Endpoints
@app.post("/api/v1/test/adversarial-attacks/start", response_model=TestResponse)
async def start_adversarial_attacks_test(request: TestRequest, background_tasks: BackgroundTasks):
    """Start an adversarial attacks test run."""
    try:
        test_id = f"adv_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        
        test_sessions[test_id] = {
            "test_id": test_id,
            "status": "initializing",
            "progress": 0,
            "current_step": "Loading adversarial attacks dataset...",
            "total_tests": 0,
            "completed_tests": 0,
            "start_time": datetime.now().isoformat(),
            "results": {},
            "captured_responses": [],
            "evaluated_responses": [],
            "error": None
        }
        
        background_tasks.add_task(
            execute_adversarial_attacks_test,
            test_id,
            test_sessions[test_id]
        )
        
        return TestResponse(
            test_id=test_id,
            status="initializing",
            message="Adversarial attacks test started successfully",
            progress=0,
            current_step="Loading adversarial attacks dataset...",
            total_tests=MAX_PROMPTS_ADVERSARIAL
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start adversarial attacks test: {str(e)}")

@app.get("/api/v1/test/adversarial-attacks/{test_id}/status", response_model=TestResponse)
async def get_adversarial_attacks_test_status(test_id: str):
    """Get the current status of an adversarial attacks test run."""
    if test_id not in test_sessions:
        raise HTTPException(status_code=404, detail="Adversarial attacks test not found")
    
    session = test_sessions[test_id]
    return TestResponse(
        test_id=test_id,
        status=session["status"],
        message=session.get("current_step", ""),
        progress=session["progress"],
        current_step=session.get("current_step", ""),
        total_tests=session["total_tests"],
        completed_tests=session["completed_tests"],
        results=session["results"]
    )

@app.get("/api/v1/test/adversarial-attacks/{test_id}/results")
async def get_adversarial_attacks_test_results(test_id: str):
    """Get the final results of a completed adversarial attacks test."""
    if test_id not in test_sessions:
        raise HTTPException(status_code=404, detail="Adversarial attacks test not found")
    
    session = test_sessions[test_id]
    if session["status"] != "completed":
        raise HTTPException(status_code=400, detail="Adversarial attacks test not completed yet")
    
    return {
        "test_id": test_id,
        "status": session["status"],
        "start_time": session["start_time"],
        "end_time": session.get("end_time"),
        "total_tests": session["total_tests"],
        "completed_tests": session["completed_tests"],
        "robustness_rate": session["results"].get("robustness_rate", 0),
        "successful_resistances": session["results"].get("successful_resistances", 0),
        "failed_attacks": session["results"].get("failed_attacks", 0),
        "total_execution_time": session["results"].get("total_execution_time"),
        "captured_responses": session["captured_responses"],
        "evaluated_responses": session["evaluated_responses"],
        "detailed_analysis": session["results"].get("detailed_analysis", {}),
        "performance_metrics": session["results"].get("performance_metrics", {})
    }

@app.get("/api/v1/test/adversarial-attacks/{test_id}/download")
async def download_adversarial_attacks_test_report(test_id: str):
    """Download the adversarial attacks test report as JSON."""
    if test_id not in test_sessions:
        raise HTTPException(status_code=404, detail="Adversarial attacks test not found")
    
    session = test_sessions[test_id]
    if session["status"] != "completed":
        raise HTTPException(status_code=400, detail="Adversarial attacks test not completed yet")
    
    report = {
        "test_metadata": {
            "test_id": test_id,
            "start_time": session["start_time"],
            "end_time": session.get("end_time"),
            "total_tests": session["total_tests"],
            "model_tested": TARGET_MODEL,
            "judge_model": JUDGE_MODEL,
            "api_key_used": "***masked***"
        },
        "summary": {
            "robustness_rate": session["results"].get("robustness_rate", 0),
            "successful_resistances": session["results"].get("successful_resistances", 0),
            "failed_attacks": session["results"].get("failed_attacks", 0),
            "total_execution_time": session["results"].get("total_execution_time", 0)
        },
        "detailed_results": session["evaluated_responses"],
        "performance_metrics": session["results"].get("performance_metrics", {}),
        "analysis": session["results"].get("detailed_analysis", {})
    }
    return report

# Firewall Input Guardrails Endpoints
@app.post("/api/v1/firewall/evaluate/input", response_model=FirewallEvaluationResponse)
async def evaluate_input(request: FirewallEvaluationRequest):
    """
    Evaluate user input for threats before sending to LLM.
    
    This endpoint runs all input guardrails detectors:
    - Prompt Injection detection
    - Jailbreak detection
    - Harmful Content detection
    - PII detection
    - Rate limiting
    
    Returns decision (allowed/blocked/sanitized/throttled) with details.
    """
    try:
        from backend.services.firewall.input_guardrails import (
            InputGuardrailsEvaluator,
            EvaluationRequest
        )
        
        # Initialize evaluator (singleton pattern - initialize once)
        if not hasattr(evaluate_input, "_evaluator"):
            evaluate_input._evaluator = InputGuardrailsEvaluator()
            await evaluate_input._evaluator.initialize()
        
        evaluator = evaluate_input._evaluator
        
        # Create evaluation request
        eval_request = EvaluationRequest(
            input_text=request.input_text,
            user_id=request.user_id,
            session_id=request.session_id,
            ip_address=request.ip_address,
            user_agent=request.user_agent,
            metadata=request.metadata,
            conversation_history=request.conversation_history,
            application_id=request.application_id
        )
        
        # Evaluate
        response = evaluator.evaluate(eval_request)
        
        # Convert to API response format
        return FirewallEvaluationResponse(
            decision=response.decision.value,
            confidence=response.confidence,
            evaluation_id=response.evaluation_id,
            latency_ms=response.latency_ms,
            threat_detected=response.threat_detected.value if response.threat_detected else None,
            severity=response.severity.value if response.severity else None,
            user_message=response.user_message,
            sanitized_input=response.sanitized_input,
            timestamp=response.timestamp,
            details=response.details
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Input evaluation failed: {str(e)}"
        )


# Firewall Chat Endpoint
@app.post("/api/v1/firewall/chat", response_model=FirewallChatResponse)
async def firewall_chat(request: FirewallChatRequest):
    """
    Raw chat endpoint - direct LLM interaction without firewall evaluation.
    
    Flow:
    1. Send user message directly to LLM (Ollama)
    2. Return LLM response
    
    This is a simple, raw chat interface with no evaluation or blocking.
    """
    from datetime import datetime
    import time
    from backend.utils.llm_client import LLMClient
    
    start_time = time.time()
    
    try:
        # Initialize LLM client for Ollama
        llm_client = LLMClient(
            provider="ollama",
            api_key=OLLAMA_API_KEY,
            host=OLLAMA_HOST
        )
        
        # Build conversation history for LLM
        messages = []
        for msg in request.conversation_history:
            if isinstance(msg, dict):
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role in ["user", "assistant"] and content:
                    messages.append({"role": role, "content": content})
        
        # Add current user message (raw, no evaluation)
        messages.append({"role": "user", "content": request.message})
        
        # Get LLM response directly
        llm_response = await llm_client.chat_completion(
            model=OLLAMA_FIREWALL_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Return response without evaluation result
        return FirewallChatResponse(
            response=llm_response,
            evaluation_result=None,  # No evaluation for raw chat
            latency_ms=latency_ms,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat request failed: {str(e)}"
        )

# Analytics Endpoints
@app.get("/api/v1/analytics/summary")
async def get_analytics_summary():
    """Get aggregated analytics summary across all test runs."""
    try:
        analytics_service = AnalyticsService()
        aggregated = analytics_service.get_aggregated_analytics()
        return aggregated
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analytics summary: {str(e)}"
        )

@app.get("/api/v1/analytics/test/{test_id}")
async def get_test_analytics(test_id: str):
    """Get analytics for a specific test run."""
    try:
        analytics_service = AnalyticsService()
        analytics = analytics_service.get_test_analytics(test_id)
        if not analytics:
            raise HTTPException(status_code=404, detail="Test analytics not found")
        return analytics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get test analytics: {str(e)}"
        )

@app.get("/api/v1/analytics/module/{module_type}")
async def get_module_analytics(module_type: str):
    """Get analytics for a specific module type."""
    try:
        analytics_service = AnalyticsService()
        module_analytics = analytics_service.get_module_analytics(module_type)
        return {
            "module_type": module_type,
            "test_runs": module_analytics,
            "count": len(module_analytics)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get module analytics: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

