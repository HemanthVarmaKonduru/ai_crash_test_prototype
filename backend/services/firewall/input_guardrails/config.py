"""
Configuration for Input Guardrails evaluation system.

This module contains all configurable parameters, thresholds, and settings
for the real-time input guardrails system.
"""
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class DetectorConfig:
    """Configuration for a single detector."""
    enabled: bool = True
    threshold: float = 0.95  # Very high threshold - only block obvious threats (user-friendly)
    action: str = "block"  # block, allow, log, sanitize
    timeout_ms: int = 50  # Maximum time for evaluation


@dataclass
class PromptInjectionConfig(DetectorConfig):
    """Configuration for prompt injection detection."""
    use_existing_evaluator: bool = True  # Reuse existing prompt injection evaluator
    enable_layer1: bool = True
    enable_layer3: bool = True  # Use LLM judge for edge cases
    techniques: Dict[str, bool] = field(default_factory=lambda: {
        "instruction_override": True,
        "role_playing": True,
        "delimiter_attack": True,
        "encoding_attack": True,
        "context_switch": True
    })


@dataclass
class JailbreakConfig(DetectorConfig):
    """Configuration for jailbreak detection."""
    use_existing_evaluator: bool = True  # Reuse existing jailbreak evaluator
    enable_layer1: bool = True
    enable_layer3: bool = True
    detect_dan_mode: bool = True
    detect_role_play: bool = True
    detect_hypothetical: bool = True


@dataclass
class HarmfulContentConfig(DetectorConfig):
    """Configuration for harmful content detection."""
    categories: Dict[str, Dict[str, any]] = field(default_factory=lambda: {
        "violence": {
            "enabled": True,
            "threshold": 0.95,  # Very high - only block obvious direct threats
            "keywords": ["bomb", "weapon", "kill", "murder", "violence", "attack", "explosive", "explosives"],
            "context_aware": False  # Disabled for user-friendliness - allow educational queries
        },
        "illegal": {
            "enabled": True,
            "threshold": 0.95,  # Very high - only block obvious direct threats
            "keywords": ["illegal", "drug", "hack", "steal", "fraud"]
        },
        "hate_speech": {
            "enabled": True,
            "threshold": 0.75,
            "keywords": ["hate", "discrimination", "racist"]
        },
        "self_harm": {
            "enabled": True,
            "threshold": 0.9,
            "keywords": ["suicide", "self harm", "hurt myself"]
        },
        "explicit": {
            "enabled": True,
            "threshold": 0.7,
            "keywords": ["explicit", "sexual", "pornographic"]
        }
    })
    use_ml_model: bool = False  # Can use Perspective API or custom model
    use_llm_judge: bool = True  # Use LLM for context-aware detection


@dataclass
class PIIConfig(DetectorConfig):
    """Configuration for PII detection."""
    pii_types: Dict[str, Dict[str, any]] = field(default_factory=lambda: {
        "ssn": {
            "enabled": True,
            "action": "sanitize",
            "pattern": r"\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b"
        },
        "credit_card": {
            "enabled": True,
            "action": "sanitize",
            "pattern": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"
        },
        "email": {
            "enabled": True,
            "action": "sanitize",
            "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        },
        "phone": {
            "enabled": True,
            "action": "sanitize",
            "pattern": r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b|\b\+?\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b"
        },
        "bank_account": {
            "enabled": True,
            "action": "block",
            "pattern": r"\b\d{8,17}\b"  # Generic bank account pattern
        }
    })
    sanitization_method: str = "redact"  # redact, mask, hash, remove
    block_if_multiple: bool = True  # Block if 3+ PII types detected
    block_if_critical: bool = True  # Block SSN, bank account, etc.


@dataclass
class RateLimitConfig(DetectorConfig):
    """Configuration for rate limiting."""
    limits: Dict[str, Dict[str, int]] = field(default_factory=lambda: {
        "per_user": {
            "rpm": 60,  # Requests per minute
            "rph": 1000,  # Requests per hour
            "rpd": 10000  # Requests per day
        },
        "per_ip": {
            "rpm": 100,
            "rph": 5000,
            "rpd": 50000
        },
        "per_session": {
            "rpm": 30,
            "rph": 500
        }
    })
    action: str = "throttle"  # block, throttle
    burst_protection: bool = True
    burst_window_ms: int = 1000
    burst_max_requests: int = 10


@dataclass
class ContextAwareConfig(DetectorConfig):
    """Configuration for context-aware detection."""
    max_conversation_history: int = 5  # Number of messages to track
    conversation_ttl_seconds: int = 3600  # 1 hour
    storage_backend: str = "memory"  # memory, redis (future)
    
    # Context adjustment multipliers (very aggressive reduction for user-friendliness)
    educational_multiplier: float = 0.1  # Very aggressive reduction - prioritize user experience
    direct_request_multiplier: float = 1.1  # Slight increase for direct requests
    escalation_multiplier: float = 1.2  # Moderate increase for escalation
    
    # Multi-turn detection
    detect_gradual_escalation: bool = True
    detect_context_switching: bool = True
    
    # Actions
    action_on_escalation: str = "block"  # block, warn, log


@dataclass
class EncodingDetectionConfig(DetectorConfig):
    """Configuration for encoding detection."""
    detect_base64: bool = True
    detect_url_encoding: bool = True
    decode_and_recheck: bool = True  # Decode and re-check decoded content
    max_decode_size: int = 10240  # 10KB max decode size
    action_on_encoding: str = "recheck"  # block, recheck, log


@dataclass
class InputGuardrailsConfig:
    """Main configuration for Input Guardrails system."""
    
    # Detector configurations
    prompt_injection: PromptInjectionConfig = field(default_factory=PromptInjectionConfig)
    jailbreak: JailbreakConfig = field(default_factory=JailbreakConfig)
    harmful_content: HarmfulContentConfig = field(default_factory=HarmfulContentConfig)
    pii: PIIConfig = field(default_factory=PIIConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    context_aware: ContextAwareConfig = field(default_factory=ContextAwareConfig)
    encoding_detection: EncodingDetectionConfig = field(default_factory=EncodingDetectionConfig)
    
    # Performance settings
    max_evaluation_time_ms: int = 50  # Target: <50ms
    parallel_detection: bool = True  # Run detectors in parallel
    early_exit_on_block: bool = True  # Stop if critical threat detected
    
    # Decision priority (if multiple threats detected)
    priority_order: List[str] = field(default_factory=lambda: [
        "rate_limit",  # Highest priority
        "encoding_detection",  # Check encoding early
        "harmful_content",
        "prompt_injection",
        "jailbreak",
        "pii",  # Lowest priority
        "context_aware"  # Applied after other detectors
    ])
    
    # Fail-safe settings
    fail_open: bool = False  # If firewall fails, allow or block?
    timeout_action: str = "block"  # block or allow on timeout
    
    # Logging
    log_all_evaluations: bool = True
    log_blocked_only: bool = False
    
    @classmethod
    def from_env(cls) -> 'InputGuardrailsConfig':
        """Create configuration from environment variables."""
        config = cls()
        
        # Allow environment variable overrides
        config.max_evaluation_time_ms = int(
            os.getenv("FIREWALL_MAX_EVAL_TIME_MS", "50")
        )
        config.parallel_detection = os.getenv(
            "FIREWALL_PARALLEL_DETECTION", "true"
        ).lower() == "true"
        config.fail_open = os.getenv(
            "FIREWALL_FAIL_OPEN", "false"
        ).lower() == "true"
        
        return config


# Default configuration instance
DEFAULT_CONFIG = InputGuardrailsConfig.from_env()

