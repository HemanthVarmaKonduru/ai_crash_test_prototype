"""
Pydantic models for API request/response schemas.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel

class TestRequest(BaseModel):
    model_provider: str
    model_name: str
    api_endpoint: str
    api_key: str
    data_type: str
    test_mode: str = "automated"

class TestResponse(BaseModel):
    test_id: str
    status: str
    message: str
    progress: int = 0
    current_step: str = ""
    total_tests: int = 0
    completed_tests: int = 0
    results: Dict[str, Any] = {}

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[Dict[str, Any]] = None

class LogoutRequest(BaseModel):
    token: str

class VerifyRequest(BaseModel):
    token: str


# Firewall Input Guardrails Schemas
class FirewallEvaluationRequest(BaseModel):
    input_text: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = {}
    conversation_history: list = []
    application_id: Optional[str] = None


class FirewallEvaluationResponse(BaseModel):
    decision: str  # allowed, blocked, sanitized, throttled
    confidence: float
    evaluation_id: str
    latency_ms: float
    threat_detected: Optional[str] = None
    severity: Optional[str] = None
    user_message: Optional[str] = None
    sanitized_input: Optional[str] = None
    timestamp: str
    details: Dict[str, Any] = {}


# Firewall Chat Schemas
class FirewallChatRequest(BaseModel):
    message: str
    conversation_history: list = []  # List of previous messages
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class FirewallChatResponse(BaseModel):
    response: str
    evaluation_result: Optional[FirewallEvaluationResponse] = None
    latency_ms: float
    timestamp: str

