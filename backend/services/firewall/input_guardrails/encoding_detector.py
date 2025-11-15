"""
Encoding Detection Detector for Input Guardrails.

Detects and decodes common encoding schemes used to evade detection:
- Base64 encoding
- URL encoding (%XX)
- Re-checks decoded content for threats
"""
import re
import time
import base64
from urllib.parse import unquote
from typing import Dict, Optional, Tuple
from .types import DetectorResult, ThreatType, Decision, SeverityLevel
from .config import EncodingDetectionConfig


class EncodingDetector:
    """
    Detects encoding-based evasion attempts.
    
    Decodes common encodings and re-checks the decoded content
    for threats.
    """
    
    def __init__(self, config: EncodingDetectionConfig):
        """
        Initialize encoding detector.
        
        Args:
            config: Encoding detection configuration
        """
        self.config = config
        self.base64_pattern = re.compile(r'[A-Za-z0-9+/=]{20,}')
        self.url_encoding_pattern = re.compile(r'%[0-9A-Fa-f]{2}')
    
    def detect_encoding(self, text: str) -> DetectorResult:
        """
        Detect and handle encoded content.
        
        Args:
            text: Input text to check
            
        Returns:
            DetectorResult with encoding detection status
        """
        start_time = time.time()
        
        if not self.config.enabled:
            return DetectorResult(
                threat_type=ThreatType.PROMPT_INJECTION,  # Default
                detected=False,
                confidence=1.0,
                severity=SeverityLevel.LOW,
                decision=Decision.ALLOWED,
                latency_ms=(time.time() - start_time) * 1000
            )
        
        detected_encodings = []
        decoded_text = text
        encoding_details = {}
        
        # Check for Base64 encoding
        if self.config.detect_base64:
            base64_matches = self._detect_base64(text)
            if base64_matches:
                detected_encodings.append("base64")
                encoding_details["base64"] = {
                    "matches": len(base64_matches),
                    "encoded_segments": base64_matches
                }
                
                # Decode Base64 segments
                if self.config.decode_and_recheck:
                    decoded_text = self._decode_base64_segments(text, base64_matches)
        
        # Check for URL encoding
        if self.config.detect_url_encoding:
            url_matches = self._detect_url_encoding(text)
            if url_matches:
                detected_encodings.append("url")
                encoding_details["url"] = {
                    "matches": len(url_matches),
                    "encoded_segments": url_matches[:5]  # Limit for details
                }
                
                # Decode URL encoding
                if self.config.decode_and_recheck:
                    decoded_text = self._decode_url_encoding(decoded_text)
        
        # Determine if encoding was detected
        detected = len(detected_encodings) > 0
        
        # If encoding detected and decode enabled, flag for re-check
        # (The actual re-check happens in the main evaluator)
        if detected and self.config.decode_and_recheck:
            # Encoding detected - decoded text should be re-checked
            # This detector flags it, main evaluator will re-check
            decision = Decision.BLOCKED if self.config.action_on_encoding == "block" else Decision.ALLOWED
        elif detected and self.config.action_on_encoding == "block":
            decision = Decision.BLOCKED
        else:
            decision = Decision.ALLOWED
        
        latency_ms = (time.time() - start_time) * 1000
        
        return DetectorResult(
            threat_type=ThreatType.PROMPT_INJECTION,  # Encoding is often used for prompt injection
            detected=detected,
            confidence=1.0 if detected else 0.0,
            severity=SeverityLevel.HIGH if detected else SeverityLevel.LOW,
            decision=decision,
            details={
                "encodings_detected": detected_encodings,
                "encoding_details": encoding_details,
                "decoded_text": decoded_text if detected and self.config.decode_and_recheck else None,
                "requires_recheck": detected and self.config.decode_and_recheck
            },
            latency_ms=latency_ms,
            reasoning=f"Detected encoding: {', '.join(detected_encodings)}" if detected else "No encoding detected"
        )
    
    def _detect_base64(self, text: str) -> list:
        """
        Detect Base64 encoded segments.
        
        Args:
            text: Input text
            
        Returns:
            List of Base64-encoded segments found
        """
        matches = []
        
        # Find potential Base64 segments
        potential_matches = self.base64_pattern.findall(text)
        
        for match in potential_matches:
            # Validate it's actually Base64
            if self._is_valid_base64(match):
                # Check if decoded content looks suspicious
                try:
                    decoded = base64.b64decode(match, validate=True).decode('utf-8', errors='ignore')
                    # If decoded content is readable and contains suspicious patterns
                    if len(decoded) > 10 and self._contains_suspicious_content(decoded):
                        matches.append(match)
                except Exception:
                    # Invalid Base64, skip
                    pass
        
        return matches
    
    def _is_valid_base64(self, text: str) -> bool:
        """
        Check if text is valid Base64.
        
        Args:
            text: Text to check
            
        Returns:
            True if valid Base64
        """
        try:
            # Check length (must be multiple of 4 after padding)
            padding = text.count('=')
            if padding > 2:
                return False
            
            # Try to decode
            decoded = base64.b64decode(text, validate=True)
            return len(decoded) > 0
        except Exception:
            return False
    
    def _detect_url_encoding(self, text: str) -> list:
        """
        Detect URL-encoded segments.
        
        Args:
            text: Input text
            
        Returns:
            List of URL-encoded segments found
        """
        matches = self.url_encoding_pattern.findall(text)
        
        # Only flag if significant encoding (at least 3 encoded chars)
        if len(matches) >= 3:
            return matches
        
        return []
    
    def _decode_base64_segments(self, text: str, segments: list) -> str:
        """
        Decode Base64 segments in text.
        
        Args:
            text: Original text
            segments: List of Base64 segments to decode
            
        Returns:
            Text with Base64 segments decoded
        """
        decoded = text
        
        for segment in segments:
            try:
                decoded_bytes = base64.b64decode(segment, validate=True)
                decoded_segment = decoded_bytes.decode('utf-8', errors='ignore')
                # Replace encoded segment with decoded version
                decoded = decoded.replace(segment, decoded_segment, 1)
            except Exception:
                # Skip invalid segments
                continue
        
        return decoded
    
    def _decode_url_encoding(self, text: str) -> str:
        """
        Decode URL encoding in text.
        
        Args:
            text: Text with URL encoding
            
        Returns:
            Decoded text
        """
        try:
            # URL decode
            decoded = unquote(text)
            return decoded
        except Exception:
            # If decoding fails, return original
            return text
    
    def _contains_suspicious_content(self, text: str) -> bool:
        """
        Check if decoded content contains suspicious patterns.
        
        Args:
            text: Decoded text
            
        Returns:
            True if suspicious
        """
        text_lower = text.lower()
        
        # Suspicious patterns that might indicate evasion
        suspicious_patterns = [
            "ignore",
            "bypass",
            "jailbreak",
            "system prompt",
            "previous instructions",
            "hack",
            "exploit"
        ]
        
        return any(pattern in text_lower for pattern in suspicious_patterns)

