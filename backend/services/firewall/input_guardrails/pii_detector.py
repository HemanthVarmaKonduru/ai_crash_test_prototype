"""
PII (Personally Identifiable Information) Detector for Input Guardrails.

Detects and handles PII in user inputs:
- SSN
- Credit card numbers
- Email addresses
- Phone numbers
- Bank account numbers
- And more...
"""
import re
import time
from typing import Dict, List, Optional
from .types import DetectorResult, ThreatType, Decision, SeverityLevel, PIIInfo
from .config import PIIConfig


class PIIDetector:
    """
    PII detection using regex patterns and validation.
    
    Supports multiple PII types with configurable actions:
    - Sanitize (redact, mask, hash, remove)
    - Block (reject the request)
    """
    
    def __init__(self, config: PIIConfig):
        """
        Initialize PII detector.
        
        Args:
            config: PII detection configuration
        """
        self.config = config
        self.patterns = self._compile_patterns()
    
    def detect_pii(self, text: str) -> DetectorResult:
        """
        Detect PII in input text.
        
        Args:
            text: Input text to check
            
        Returns:
            DetectorResult with PII detection status
        """
        start_time = time.time()
        
        if not self.config.enabled:
            return DetectorResult(
                threat_type=ThreatType.PII,
                detected=False,
                confidence=1.0,
                severity=SeverityLevel.LOW,
                decision=Decision.ALLOWED,
                latency_ms=(time.time() - start_time) * 1000
            )
        
        detected_types = []
        detected_values = {}
        sanitized_text = text
        sanitization_changes = []
        
        # Check each PII type
        for pii_type, pii_config in self.config.pii_types.items():
            if not pii_config.get("enabled", True):
                continue
            
            pattern = self.patterns.get(pii_type)
            if not pattern:
                continue
            
            matches = pattern.findall(text)
            if matches:
                detected_types.append(pii_type)
                detected_values[pii_type] = matches
                
                # Sanitize if action is sanitize
                if pii_config.get("action") == "sanitize":
                    sanitized_text, changes = self._sanitize(
                        sanitized_text,
                        matches,
                        pii_type,
                        pii_config
                    )
                    sanitization_changes.extend(changes)
        
        # Determine decision
        detected = len(detected_types) > 0
        decision = Decision.ALLOWED
        severity = SeverityLevel.LOW
        
        if detected:
            # Check if should block
            critical_types = ["ssn", "bank_account", "passport"]
            has_critical = any(t in critical_types for t in detected_types)
            
            if self.config.block_if_critical and has_critical:
                decision = Decision.BLOCKED
                severity = SeverityLevel.CRITICAL
            elif self.config.block_if_multiple and len(detected_types) >= 3:
                decision = Decision.BLOCKED
                severity = SeverityLevel.HIGH
            else:
                # Check action for detected types
                block_actions = [
                    self.config.pii_types[t].get("action") == "block"
                    for t in detected_types
                ]
                if any(block_actions):
                    decision = Decision.BLOCKED
                    severity = SeverityLevel.MEDIUM
                else:
                    decision = Decision.SANITIZED
                    severity = SeverityLevel.MEDIUM
        
        latency_ms = (time.time() - start_time) * 1000
        
        pii_info = PIIInfo(
            detected_types=detected_types,
            detected_values=detected_values,
            sanitized_text=sanitized_text if decision == Decision.SANITIZED else None,
            sanitization_changes=sanitization_changes
        )
        
        return DetectorResult(
            threat_type=ThreatType.PII,
            detected=detected,
            confidence=1.0 if detected else 0.0,
            severity=severity,
            decision=decision,
            details={
                "pii_info": {
                    "detected_types": pii_info.detected_types,
                    "detected_values": {k: len(v) for k, v in pii_info.detected_values.items()},
                    "sanitized_text": pii_info.sanitized_text,
                    "sanitization_changes": len(pii_info.sanitization_changes)
                }
            },
            latency_ms=latency_ms,
            reasoning=f"Detected {len(detected_types)} PII type(s): {', '.join(detected_types)}" if detected else "No PII detected"
        )
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for PII detection."""
        patterns = {}
        
        for pii_type, pii_config in self.config.pii_types.items():
            pattern_str = pii_config.get("pattern")
            if pattern_str:
                try:
                    patterns[pii_type] = re.compile(pattern_str, re.IGNORECASE)
                except re.error:
                    # Skip invalid patterns
                    continue
        
        return patterns
    
    def _sanitize(
        self,
        text: str,
        matches: List[str],
        pii_type: str,
        pii_config: Dict
    ):
        """
        Sanitize PII in text.
        
        Args:
            text: Text to sanitize
            matches: List of matched PII values
            pii_type: Type of PII
            pii_config: Configuration for this PII type
            
        Returns:
            Tuple of (sanitized_text, changes_list)
        """
        method = self.config.sanitization_method
        sanitized = text
        changes = []
        
        for match in matches:
            original = match
            
            if method == "redact":
                replacement = f"[{pii_type.upper()}]"
            elif method == "mask":
                # Show partial (e.g., ***-1234 for SSN)
                if pii_type == "ssn":
                    replacement = f"***-**-{match[-4:]}" if len(match) >= 4 else "[SSN]"
                elif pii_type == "credit_card":
                    replacement = f"****-****-****-{match[-4:]}" if len(match) >= 4 else "[CARD]"
                elif pii_type == "phone":
                    replacement = f"***-***-{match[-4:]}" if len(match) >= 4 else "[PHONE]"
                else:
                    replacement = f"[{pii_type.upper()}]"
            elif method == "hash":
                import hashlib
                replacement = hashlib.sha256(match.encode()).hexdigest()[:8]
            elif method == "remove":
                replacement = ""
            else:
                replacement = f"[{pii_type.upper()}]"
            
            sanitized = sanitized.replace(original, replacement)
            changes.append({
                "type": pii_type,
                "original": original,
                "replacement": replacement
            })
        
        return sanitized, changes

