"""
Main Input Guardrails Evaluator.

Orchestrates all threat detectors and makes final decisions.
Runs detectors in parallel for maximum performance.
"""
import time
import uuid
import asyncio
from typing import List, Optional
from datetime import datetime

from .types import (
    EvaluationRequest,
    EvaluationResponse,
    DetectorResult,
    ThreatType,
    Decision,
    SeverityLevel
)
from .config import InputGuardrailsConfig, DEFAULT_CONFIG
from .response_messages import ResponseMessages
from .rate_limiter import RateLimiter
from .pii_detector import PIIDetector
from .harmful_content_detector import HarmfulContentDetector
from .prompt_injection_detector import PromptInjectionDetector
from .jailbreak_detector import JailbreakDetector
from .encoding_detector import EncodingDetector
from .context_aware_detector import ContextAwareDetector


class InputGuardrailsEvaluator:
    """
    Main orchestrator for Input Guardrails evaluation.
    
    Coordinates all threat detectors and makes final decisions based on
    priority order and detected threats.
    """
    
    def __init__(self, config: Optional[InputGuardrailsConfig] = None):
        """
        Initialize Input Guardrails evaluator.
        
        Args:
            config: Configuration for input guardrails (uses default if None)
        """
        self.config = config or DEFAULT_CONFIG
        
        # Initialize detectors
        self.rate_limiter = RateLimiter(self.config.rate_limit)
        self.encoding_detector = EncodingDetector(self.config.encoding_detection)
        self.pii_detector = PIIDetector(self.config.pii)
        self.harmful_content_detector = HarmfulContentDetector(self.config.harmful_content)
        self.prompt_injection_detector = PromptInjectionDetector(self.config.prompt_injection)
        self.jailbreak_detector = JailbreakDetector(self.config.jailbreak)
        self.context_aware_detector = ContextAwareDetector(self.config.context_aware)
        
        # Initialize prompt injection detector (async)
        self._initialized = False
    
    async def initialize(self):
        """Initialize async components."""
        if not self._initialized:
            await self.prompt_injection_detector.initialize()
            self._initialized = True
    
    def evaluate(self, request: EvaluationRequest) -> EvaluationResponse:
        """
        Evaluate input for threats.
        
        This is the main entry point. Runs all detectors and makes final decision.
        
        Args:
            request: Evaluation request with input text and metadata
            
        Returns:
            EvaluationResponse with decision and details
        """
        start_time = time.time()
        evaluation_id = f"eval_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # Step 1: Check encoding first (decode if needed)
        encoding_result = None
        text_to_check = request.input_text
        
        if self.config.encoding_detection.enabled:
            encoding_result = self.encoding_detector.detect_encoding(request.input_text)
            if encoding_result.detected and encoding_result.details.get("requires_recheck"):
                # Use decoded text for further checks
                decoded = encoding_result.details.get("decoded_text")
                if decoded:
                    text_to_check = decoded
                    # Update request with decoded text
                    request = EvaluationRequest(
                        input_text=decoded,
                        user_id=request.user_id,
                        session_id=request.session_id,
                        ip_address=request.ip_address,
                        user_agent=request.user_agent,
                        metadata={**request.metadata, "was_decoded": True, "original_encoding": encoding_result.details.get("encodings_detected")},
                        conversation_history=request.conversation_history,
                        application_id=request.application_id
                    )
        
        # Step 2: Run all other detectors (in parallel if enabled)
        if self.config.parallel_detection:
            detector_results = self._run_detectors_parallel(request, text_to_check)
        else:
            detector_results = self._run_detectors_sequential(request, text_to_check)
        
        # Add encoding result if available
        if encoding_result:
            detector_results.append(encoding_result)
        
        # Step 3: Apply context-aware analysis (enhances other detectors)
        context_adjusted_results = self._apply_context_aware_analysis(
            detector_results,
            request,
            text_to_check
        )
        
        # Step 4: Make final decision based on priority
        decision_result = self._make_decision(context_adjusted_results, request)
        
        # Calculate total latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Build response (use context-adjusted results for display)
        response = EvaluationResponse(
            decision=decision_result["decision"],
            confidence=decision_result["confidence"],
            evaluation_id=evaluation_id,
            latency_ms=latency_ms,
            threat_detected=decision_result.get("threat_type"),
            severity=decision_result.get("severity"),
            user_message=decision_result.get("user_message"),
            sanitized_input=decision_result.get("sanitized_input"),
            detector_results=context_adjusted_results,
            details={
                "total_detectors_run": len(detector_results),
                "threats_detected": [
                    r.threat_type.value for r in detector_results if r.detected
                ],
                "priority_order": self.config.priority_order,
                "was_decoded": request.metadata.get("was_decoded", False),
                "original_encoding": request.metadata.get("original_encoding", [])
            }
        )
        
        return response
    
    def _apply_context_aware_analysis(
        self,
        detector_results: List[DetectorResult],
        request: EvaluationRequest,
        text: str
    ) -> List[DetectorResult]:
        """
        Apply context-aware analysis to adjust detector results.
        
        Args:
            detector_results: Results from all detectors
            request: Evaluation request
            text: Text being evaluated
            
        Returns:
            List of detector results with context adjustments
        """
        if not self.config.context_aware.enabled:
            return detector_results
        
        adjusted_results = []
        
        for result in detector_results:
            # Skip context-aware for rate limiting and encoding
            if result.threat_type in [ThreatType.RATE_LIMIT]:
                adjusted_results.append(result)
                continue
            
            # Apply context-aware analysis
            context_result = self.context_aware_detector.analyze_with_context(
                input_text=text,
                user_id=request.user_id,
                session_id=request.session_id,
                base_confidence=result.confidence,
                threat_type=result.threat_type
            )
            
            # Use context-adjusted confidence if higher, or if context detected threat
            if context_result.detected or context_result.confidence > result.confidence:
                # Update result with context adjustments
                result.confidence = context_result.confidence
                result.detected = result.detected or context_result.detected
                result.severity = context_result.severity
                result.details.update(context_result.details)
            
            # Ensure decision matches detected status
            if result.detected and result.decision == Decision.ALLOWED:
                # If threat detected, decision should be BLOCKED (unless it's PII which can be SANITIZED)
                if result.threat_type != ThreatType.PII:
                    result.decision = Decision.BLOCKED
                elif result.decision != Decision.SANITIZED:
                    result.decision = Decision.BLOCKED
            
            adjusted_results.append(result)
        
        return adjusted_results
    
    def _run_detectors_parallel(self, request: EvaluationRequest, text: str) -> List[DetectorResult]:
        """
        Run all detectors in parallel for maximum performance.
        
        Args:
            request: Evaluation request
            
        Returns:
            List of detector results
        """
        # Create tasks for all detectors
        tasks = []
        
        # Rate limiter (highest priority - check first)
        if self.config.rate_limit.enabled:
            tasks.append(("rate_limit", self.rate_limiter.check_rate_limit(
                user_id=request.user_id,
                ip_address=request.ip_address,
                session_id=request.session_id
            )))
        
        # Other detectors (can run in parallel)
        if self.config.prompt_injection.enabled:
            tasks.append(("prompt_injection", self.prompt_injection_detector.detect_prompt_injection(
                text
            )))
        
        if self.config.jailbreak.enabled:
            tasks.append(("jailbreak", self.jailbreak_detector.detect_jailbreak(
                text
            )))
        
        if self.config.harmful_content.enabled:
            tasks.append(("harmful_content", self.harmful_content_detector.detect_harmful_content(
                text
            )))
        
        if self.config.pii.enabled:
            tasks.append(("pii", self.pii_detector.detect_pii(
                text
            )))
        
        # Early exit if rate limit exceeded (highest priority)
        if tasks and tasks[0][0] == "rate_limit":
            rate_result = tasks[0][1]
            if rate_result.detected:
                # Return rate limit result immediately
                return [rate_result]
        
        # Return all results
        return [result for _, result in tasks]
    
    def _run_detectors_sequential(self, request: EvaluationRequest, text: str) -> List[DetectorResult]:
        """
        Run detectors sequentially (fallback if parallel disabled).
        
        Args:
            request: Evaluation request
            
        Returns:
            List of detector results
        """
        results = []
        
        # Rate limiter first (highest priority)
        if self.config.rate_limit.enabled:
            rate_result = self.rate_limiter.check_rate_limit(
                user_id=request.user_id,
                ip_address=request.ip_address,
                session_id=request.session_id
            )
            results.append(rate_result)
            
            # Early exit if rate limited
            if rate_result.detected and self.config.early_exit_on_block:
                return results
        
        # Other detectors
        if self.config.prompt_injection.enabled:
            results.append(self.prompt_injection_detector.detect_prompt_injection(
                text
            ))
        
        if self.config.jailbreak.enabled:
            results.append(self.jailbreak_detector.detect_jailbreak(
                text
            ))
        
        if self.config.harmful_content.enabled:
            results.append(self.harmful_content_detector.detect_harmful_content(
                text
            ))
        
        if self.config.pii.enabled:
            results.append(self.pii_detector.detect_pii(
                text
            ))
        
        return results
    
    def _make_decision(
        self,
        detector_results: List[DetectorResult],
        request: EvaluationRequest
    ) -> dict:
        """
        Make final decision based on detector results and priority.
        
        Args:
            detector_results: Results from all detectors
            request: Original evaluation request
            
        Returns:
            Dict with final decision, confidence, threat type, etc.
        """
        # Filter to only detected threats
        detected_threats = [r for r in detector_results if r.detected]
        
        if not detected_threats:
            return {
                "decision": Decision.ALLOWED,
                "confidence": 1.0,
                "threat_type": None,
                "severity": SeverityLevel.LOW,
                "user_message": None,
                "sanitized_input": None
            }
        
        # Sort by priority order
        priority_map = {
            threat_type: idx
            for idx, threat_type in enumerate(self.config.priority_order)
        }
        
        detected_threats.sort(
            key=lambda r: priority_map.get(r.threat_type.value, 999)
        )
        
        # Get highest priority threat
        primary_threat = detected_threats[0]
        
        # USER-FRIENDLY DECISION LOGIC: Only block when extremely confident
        # Prioritize user experience - allow edge cases to pass through
        min_blocking_confidence = 0.92  # Very high threshold - only block obvious threats
        
        # If confidence is below threshold, allow the request (user-friendly)
        if primary_threat.confidence < min_blocking_confidence:
            return {
                "decision": Decision.ALLOWED,
                "confidence": primary_threat.confidence,
                "threat_type": primary_threat.threat_type,
                "severity": primary_threat.severity,
                "user_message": None,
                "sanitized_input": None
            }
        
        # For any educational/legitimate context, be very lenient
        # Check if context-aware analysis reduced confidence or if it's educational
        context_details = primary_threat.details.get("context_analysis", {})
        if context_details.get("is_educational") or primary_threat.confidence < 0.80:
            # Educational context or low confidence = allow (user-friendly)
            return {
                "decision": Decision.ALLOWED,
                "confidence": primary_threat.confidence,
                "threat_type": primary_threat.threat_type,
                "severity": primary_threat.severity,
                "user_message": None,
                "sanitized_input": None
            }
        
        # Determine decision based on threat type
        decision = primary_threat.decision
        user_message = None
        sanitized_input = None
        
        # Handle PII sanitization
        if primary_threat.threat_type == ThreatType.PII:
            pii_info = primary_threat.details.get("pii_info", {})
            if decision == Decision.SANITIZED:
                sanitized_input = pii_info.get("sanitized_text")
                user_message = ResponseMessages.PII_SANITIZED
            elif decision == Decision.BLOCKED:
                user_message = ResponseMessages.PII_BLOCKED
        
        # Handle rate limiting
        elif primary_threat.threat_type == ThreatType.RATE_LIMIT:
            user_message = ResponseMessages.RATE_LIMIT_EXCEEDED
        
        # Handle harmful content
        elif primary_threat.threat_type == ThreatType.HARMFUL_CONTENT:
            categories = primary_threat.details.get("categories", [])
            category = categories[0] if categories else "generic"
            user_message = ResponseMessages.get_message_for_harmful_content(category)
        
        # Handle prompt injection / jailbreak
        elif primary_threat.threat_type in [ThreatType.PROMPT_INJECTION, ThreatType.JAILBREAK]:
            user_message = ResponseMessages.get_message_for_threat(
                primary_threat.threat_type.value,
                primary_threat.severity.value
            )
        
        # Default message
        if not user_message:
            user_message = ResponseMessages.GENERIC_BLOCKED
        
        return {
            "decision": decision,
            "confidence": primary_threat.confidence,
            "threat_type": primary_threat.threat_type,
            "severity": primary_threat.severity,
            "user_message": user_message,
            "sanitized_input": sanitized_input
        }

