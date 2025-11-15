"""
Type definitions for Input Guardrails evaluation system.

This module provides all type hints and data structures used throughout
the input guardrails system to ensure type safety and code clarity.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class ThreatType(str, Enum):
    """Types of threats that can be detected."""
    PROMPT_INJECTION = "prompt_injection"
    JAILBREAK = "jailbreak"
    HARMFUL_CONTENT = "harmful_content"
    PII = "pii"
    RATE_LIMIT = "rate_limit"


class Decision(str, Enum):
    """Possible evaluation decisions."""
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    SANITIZED = "sanitized"
    THROTTLED = "throttled"


class SeverityLevel(str, Enum):
    """Severity levels for detected threats."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DetectorResult:
    """Result from a single threat detector."""
    threat_type: ThreatType
    detected: bool
    confidence: float  # 0.0 to 1.0
    severity: SeverityLevel
    decision: Decision
    details: Dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0
    reasoning: str = ""


@dataclass
class EvaluationRequest:
    """Request for input evaluation."""
    input_text: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[str] = field(default_factory=list)
    application_id: Optional[str] = None


@dataclass
class EvaluationResponse:
    """Response from input evaluation."""
    decision: Decision
    confidence: float
    evaluation_id: str
    latency_ms: float
    threat_detected: Optional[ThreatType] = None
    severity: Optional[SeverityLevel] = None
    user_message: Optional[str] = None  # Static response message
    sanitized_input: Optional[str] = None
    detector_results: List[DetectorResult] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RateLimitInfo:
    """Rate limiting information."""
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    requests_remaining: int = 0
    reset_at: Optional[datetime] = None
    exceeded: bool = False


@dataclass
class PIIInfo:
    """PII detection information."""
    detected_types: List[str] = field(default_factory=list)
    detected_values: Dict[str, List[str]] = field(default_factory=dict)
    sanitized_text: Optional[str] = None
    sanitization_changes: List[Dict[str, str]] = field(default_factory=list)

