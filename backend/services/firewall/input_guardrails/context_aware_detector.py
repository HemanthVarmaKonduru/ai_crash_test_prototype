"""
Context-Aware Detector for Input Guardrails.

Uses conversation history to:
- Reduce false positives (understand context)
- Detect multi-turn attacks (gradual escalation)
- Adjust threat confidence based on context
"""
import time
from typing import Dict, List, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta
from .types import DetectorResult, ThreatType, Decision, SeverityLevel
from .config import ContextAwareConfig


class ContextAwareDetector:
    """
    Context-aware detection using conversation history.
    
    Tracks conversation state and adjusts threat detection
    based on context and conversation patterns.
    """
    
    def __init__(self, config: ContextAwareConfig):
        """
        Initialize context-aware detector.
        
        Args:
            config: Context-aware configuration
        """
        self.config = config
        
        # In-memory conversation storage
        # Key: user_id or session_id, Value: deque of messages
        self.conversation_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=config.max_conversation_history))
        
        # Track dangerous keywords across conversation
        self.keyword_tracking: Dict[str, List[str]] = defaultdict(list)
        
        # Cleanup old conversations periodically
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # 5 minutes
    
    def analyze_with_context(
        self,
        input_text: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        base_confidence: float = 0.0,
        threat_type: Optional[ThreatType] = None
    ) -> DetectorResult:
        """
        Analyze input with conversation context.
        
        Args:
            input_text: Current input text
            user_id: User identifier
            session_id: Session identifier
            base_confidence: Confidence from other detectors
            threat_type: Detected threat type (if any)
            
        Returns:
            DetectorResult with context-adjusted confidence
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
        
        # Get conversation identifier
        identifier = user_id or session_id or "anonymous"
        
        # Get conversation history
        history = list(self.conversation_history[identifier])
        
        # Cleanup old conversations periodically
        self._cleanup_old_conversations()
        
        # Analyze context
        context_analysis = self._analyze_context(input_text, history)
        
        # Adjust confidence based on context
        adjusted_confidence = self._adjust_confidence(
            base_confidence,
            context_analysis,
            input_text,
            history
        )
        
        # Detect multi-turn patterns
        multi_turn_threat = self._detect_multi_turn_threats(
            input_text,
            history,
            identifier
        )
        
        # Update conversation history
        self._update_history(identifier, input_text)
        
        # Determine if context indicates threat
        detected = False
        if multi_turn_threat["detected"]:
            detected = True
            adjusted_confidence = max(adjusted_confidence, multi_turn_threat["confidence"])
        elif base_confidence > 0:
            # If base detector found something, use adjusted confidence
            # Context can reduce confidence (educational) or increase it (direct request)
            detected = adjusted_confidence >= 0.7
        else:
            # No base threat, but check if context alone detected threat
            detected = multi_turn_threat["detected"]
            if detected:
                adjusted_confidence = multi_turn_threat["confidence"]
        
        latency_ms = (time.time() - start_time) * 1000
        
        return DetectorResult(
            threat_type=threat_type or ThreatType.PROMPT_INJECTION,
            detected=detected,
            confidence=adjusted_confidence,
            severity=self._determine_severity(adjusted_confidence, multi_turn_threat),
            decision=Decision.BLOCKED if detected else Decision.ALLOWED,
            details={
                "context_analysis": context_analysis,
                "multi_turn_threat": multi_turn_threat,
                "conversation_length": len(history),
                "confidence_adjustment": adjusted_confidence - base_confidence
            },
            latency_ms=latency_ms,
            reasoning=multi_turn_threat.get("reasoning", "Context-aware analysis")
        )
    
    def _analyze_context(self, text: str, history: List[str]) -> Dict:
        """
        Analyze context of the input.
        
        Args:
            text: Input text
            history: Conversation history
            
        Returns:
            Dict with context analysis
        """
        text_lower = text.lower()
        
        # Check for educational context (expanded)
        educational_indicators = [
            "explain how",
            "explain the",
            "what is",
            "tell me about",
            "for my research",
            "for my paper",
            "for my thesis",
            "for my book",
            "writing a book",
            "writing a paper",
            "in a story",
            "historical context",
            "how does it work",
            "history of",
            "chemistry of",
            "physics behind",
            "difference between",
            "ethical hacking",
            "ethical security",
            "protect against",
            "how do",
            "how do hackers",
            "how do experts",
            "latest",
            "recent",
            "in the news",
            "incident in",
            "cyber attack",
            "hacking incident",
        ]
        
        is_educational = any(indicator in text_lower for indicator in educational_indicators)
        
        # Check for direct request context
        direct_request_indicators = [
            "how to make",
            "how to create",
            "how to build",
            "tell me how to",
            "show me how to",
            "i want to",
            "i need to",
        ]
        
        is_direct_request = any(indicator in text_lower for indicator in direct_request_indicators)
        
        # Check for hypothetical context
        hypothetical_indicators = [
            "hypothetically",
            "what if",
            "suppose",
            "imagine",
            "in a hypothetical",
        ]
        
        is_hypothetical = any(indicator in text_lower for indicator in hypothetical_indicators)
        
        # Analyze conversation progression
        progression = self._analyze_progression(text, history)
        
        return {
            "is_educational": is_educational,
            "is_direct_request": is_direct_request,
            "is_hypothetical": is_hypothetical,
            "progression": progression,
            "context_type": self._determine_context_type(
                is_educational, is_direct_request, is_hypothetical
            )
        }
    
    def _analyze_progression(self, text: str, history: List[str]) -> Dict:
        """
        Analyze conversation progression for escalation patterns.
        
        Args:
            text: Current input
            history: Conversation history
            
        Returns:
            Dict with progression analysis
        """
        if not history:
            return {
                "escalation_detected": False,
                "escalation_score": 0.0,
                "topic_changes": 0
            }
        
        # Dangerous keywords to track
        dangerous_keywords = [
            "bomb", "weapon", "hack", "kill", "violence",
            "illegal", "explosive", "attack", "harmful"
        ]
        
        # Count dangerous keywords in history
        history_keywords = []
        for msg in history:
            # Handle both string and dict formats
            msg_text = msg if isinstance(msg, str) else msg.get("text", "")
            msg_lower = msg_text.lower()
            for keyword in dangerous_keywords:
                if keyword in msg_lower:
                    history_keywords.append(keyword)
        
        # Count dangerous keywords in current text
        text_lower = text.lower()
        current_keywords = [kw for kw in dangerous_keywords if kw in text_lower]
        
        # Calculate escalation
        escalation_score = 0.0
        if history_keywords and current_keywords:
            # Escalation: dangerous keywords appearing across conversation
            escalation_score = min(1.0, len(history_keywords) * 0.2 + len(current_keywords) * 0.3)
        
        # Detect topic changes
        topic_changes = 0
        if len(history) >= 2:
            # Simple heuristic: if topics are very different
            # (This is simplified - could be enhanced with topic modeling)
            pass
        
        return {
            "escalation_detected": escalation_score >= 0.5,
            "escalation_score": escalation_score,
            "topic_changes": topic_changes,
            "dangerous_keywords_in_history": len(set(history_keywords)),
            "dangerous_keywords_current": len(set(current_keywords))
        }
    
    def _adjust_confidence(
        self,
        base_confidence: float,
        context_analysis: Dict,
        text: str,
        history: List[str]
    ) -> float:
        """
        Adjust threat confidence based on context.
        
        Args:
            base_confidence: Base confidence from other detectors
            context_analysis: Context analysis results
            text: Input text
            history: Conversation history
            
        Returns:
            Adjusted confidence score
        """
        if base_confidence == 0:
            return 0.0
        
        adjusted = base_confidence
        multiplier = 1.0
        
        # Educational context reduces threat very aggressively (user-friendly)
        if context_analysis["is_educational"]:
            # Extremely aggressive reduction for educational queries
            # Prioritize user experience - allow educational queries
            # With educational_multiplier = 0.1, this becomes 0.1 * 0.2 = 0.02 (98% reduction)
            multiplier *= self.config.educational_multiplier * 0.2  # Additional 80% reduction
        
        # Direct requests increase threat
        if context_analysis["is_direct_request"]:
            multiplier *= self.config.direct_request_multiplier
        
        # Hypothetical + dangerous content is still dangerous
        if context_analysis["is_hypothetical"]:
            # Check if dangerous keywords present
            dangerous_keywords = ["bomb", "weapon", "hack", "kill", "explosive"]
            text_lower = text.lower()
            if any(kw in text_lower for kw in dangerous_keywords):
                # Even hypothetical, dangerous content is still dangerous
                multiplier *= 0.9  # Slight reduction, but still high
            else:
                # Hypothetical without dangerous content - reduce more
                multiplier *= 0.7
        
        # Escalation increases threat
        if context_analysis["progression"]["escalation_detected"]:
            multiplier *= self.config.escalation_multiplier
        
        adjusted = base_confidence * multiplier
        
        # Clamp to valid range
        return max(0.0, min(1.0, adjusted))
    
    def _detect_multi_turn_threats(
        self,
        text: str,
        history: List[str],
        identifier: str
    ) -> Dict:
        """
        Detect multi-turn attack patterns.
        
        Args:
            text: Current input
            history: Conversation history
            identifier: User/session identifier
            
        Returns:
            Dict with multi-turn threat detection
        """
        if len(history) < 2:
            return {
                "detected": False,
                "confidence": 0.0,
                "reasoning": "Insufficient conversation history"
            }
        
        # Track dangerous keywords across conversation
        dangerous_keywords = [
            "bomb", "weapon", "hack", "kill", "violence",
            "illegal", "explosive", "attack", "harmful",
            "ignore", "bypass", "jailbreak"
        ]
        
        # Check for gradual escalation
        keyword_counts = []
        for msg in history + [text]:
            # Handle both string and dict formats
            msg_text = msg if isinstance(msg, str) else msg.get("text", "")
            msg_lower = msg_text.lower()
            count = sum(1 for kw in dangerous_keywords if kw in msg_lower)
            keyword_counts.append(count)
        
        # Detect escalation pattern
        if len(keyword_counts) >= 3:
            # Check if keywords are increasing
            if keyword_counts[-1] > keyword_counts[0] and keyword_counts[-1] > 0:
                escalation_ratio = keyword_counts[-1] / max(1, sum(keyword_counts[:-1]))
                if escalation_ratio >= 0.5:
                    return {
                        "detected": True,
                        "confidence": min(0.95, 0.7 + escalation_ratio * 0.25),
                        "reasoning": "Gradual escalation detected across conversation"
                    }
        
        # Check for context switching (normal → attack)
        if len(history) >= 2:
            # First messages are normal, last message is attack
            first_msgs_text = []
            for msg in history[:2]:
                msg_text = msg if isinstance(msg, str) else msg.get("text", "")
                first_msgs_text.append(msg_text)
            first_msgs = " ".join(first_msgs_text).lower()
            last_msg = text.lower()
            
            # Check if first messages are safe but last is dangerous
            safe_indicators = ["hello", "hi", "help", "question"]
            attack_indicators = ["ignore", "bypass", "jailbreak", "hack"]
            
            if any(ind in first_msgs for ind in safe_indicators):
                if any(ind in last_msg for ind in attack_indicators):
                    return {
                        "detected": True,
                        "confidence": 0.85,
                        "reasoning": "Context switching detected: safe conversation → attack"
                    }
        
        return {
            "detected": False,
            "confidence": 0.0,
            "reasoning": "No multi-turn threat patterns detected"
        }
    
    def _determine_context_type(
        self,
        is_educational: bool,
        is_direct_request: bool,
        is_hypothetical: bool
    ) -> str:
        """Determine the primary context type."""
        if is_educational:
            return "educational"
        elif is_direct_request:
            return "direct_request"
        elif is_hypothetical:
            return "hypothetical"
        else:
            return "neutral"
    
    def _determine_severity(
        self,
        confidence: float,
        multi_turn_threat: Dict
    ) -> SeverityLevel:
        """Determine severity based on confidence and multi-turn threat."""
        if multi_turn_threat.get("detected", False):
            if confidence >= 0.9:
                return SeverityLevel.CRITICAL
            elif confidence >= 0.8:
                return SeverityLevel.HIGH
            else:
                return SeverityLevel.MEDIUM
        
        if confidence >= 0.9:
            return SeverityLevel.CRITICAL
        elif confidence >= 0.8:
            return SeverityLevel.HIGH
        elif confidence >= 0.7:
            return SeverityLevel.MEDIUM
        else:
            return SeverityLevel.LOW
    
    def _update_history(self, identifier: str, text: str):
        """Update conversation history."""
        self.conversation_history[identifier].append({
            "text": text,
            "timestamp": time.time()
        })
    
    def _cleanup_old_conversations(self):
        """Cleanup old conversations to prevent memory leak."""
        current_time = time.time()
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        # Remove conversations older than TTL
        cutoff_time = current_time - self.config.conversation_ttl_seconds
        to_remove = []
        
        for identifier, messages in self.conversation_history.items():
            if messages and messages[0].get("timestamp", 0) < cutoff_time:
                to_remove.append(identifier)
        
        for identifier in to_remove:
            del self.conversation_history[identifier]
            if identifier in self.keyword_tracking:
                del self.keyword_tracking[identifier]
        
        self._last_cleanup = current_time
    
    def clear_history(self, identifier: str):
        """Clear conversation history for an identifier (for testing/admin)."""
        if identifier in self.conversation_history:
            del self.conversation_history[identifier]
        if identifier in self.keyword_tracking:
            del self.keyword_tracking[identifier]

