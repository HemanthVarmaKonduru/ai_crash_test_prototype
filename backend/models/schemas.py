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



