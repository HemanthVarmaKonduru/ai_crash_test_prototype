"""
Rate Limiting Detector for Input Guardrails.

Implements multi-dimensional rate limiting:
- Per user ID
- Per IP address
- Per session
- Burst protection
"""
import time
from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from .types import DetectorResult, ThreatType, Decision, SeverityLevel, RateLimitInfo
from .config import RateLimitConfig


class RateLimiter:
    """
    Rate limiting detector with sliding window algorithm.
    
    Uses in-memory storage for fast lookups. In production, this should
    be backed by Redis or similar distributed cache.
    """
    
    def __init__(self, config: RateLimitConfig):
        """
        Initialize rate limiter.
        
        Args:
            config: Rate limiting configuration
        """
        self.config = config
        
        # In-memory storage (use Redis in production)
        self.user_requests: Dict[str, list] = defaultdict(list)
        self.ip_requests: Dict[str, list] = defaultdict(list)
        self.session_requests: Dict[str, list] = defaultdict(list)
        
        # Burst protection
        self.burst_windows: Dict[str, list] = defaultdict(list)
    
    def check_rate_limit(
        self,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> DetectorResult:
        """
        Check if request exceeds rate limits.
        
        Args:
            user_id: User identifier
            ip_address: IP address
            session_id: Session identifier
            
        Returns:
            DetectorResult with rate limit status
        """
        start_time = time.time()
        
        if not self.config.enabled:
            return DetectorResult(
                threat_type=ThreatType.RATE_LIMIT,
                detected=False,
                confidence=1.0,
                severity=SeverityLevel.LOW,
                decision=Decision.ALLOWED,
                latency_ms=(time.time() - start_time) * 1000
            )
        
        current_time = time.time()
        exceeded = False
        limit_type = None
        requests_remaining = 0
        
        # Check burst protection first (fastest check)
        if self.config.burst_protection:
            identifier = user_id or ip_address or session_id or "anonymous"
            if self._check_burst(identifier, current_time):
                exceeded = True
                limit_type = "burst"
        
        # Check per-user limits
        if not exceeded and user_id:
            exceeded, remaining = self._check_limit(
                user_id,
                self.user_requests,
                self.config.limits["per_user"],
                current_time
            )
            if exceeded:
                limit_type = "per_user"
            else:
                requests_remaining = remaining
        
        # Check per-IP limits
        if not exceeded and ip_address:
            exceeded, remaining = self._check_limit(
                ip_address,
                self.ip_requests,
                self.config.limits["per_ip"],
                current_time
            )
            if exceeded:
                limit_type = "per_ip"
            else:
                requests_remaining = remaining
        
        # Check per-session limits
        if not exceeded and session_id:
            exceeded, remaining = self._check_limit(
                session_id,
                self.session_requests,
                self.config.limits["per_session"],
                current_time
            )
            if exceeded:
                limit_type = "per_session"
            else:
                requests_remaining = remaining
        
        # Record request if not exceeded
        if not exceeded:
            if user_id:
                self.user_requests[user_id].append(current_time)
            if ip_address:
                self.ip_requests[ip_address].append(current_time)
            if session_id:
                self.session_requests[session_id].append(current_time)
        
        latency_ms = (time.time() - start_time) * 1000
        
        return DetectorResult(
            threat_type=ThreatType.RATE_LIMIT,
            detected=exceeded,
            confidence=1.0 if exceeded else 0.0,
            severity=SeverityLevel.MEDIUM if exceeded else SeverityLevel.LOW,
            decision=Decision.THROTTLED if exceeded else Decision.ALLOWED,
            details={
                "limit_type": limit_type,
                "requests_remaining": requests_remaining,
                "exceeded": exceeded
            },
            latency_ms=latency_ms,
            reasoning=f"Rate limit {'exceeded' if exceeded else 'within limits'}"
        )
    
    def _check_limit(
        self,
        identifier: str,
        request_history: Dict[str, list],
        limits: Dict[str, int],
        current_time: float
    ):
        """
        Check if identifier exceeds limits using sliding window.
        
        Args:
            identifier: User/IP/Session identifier
            request_history: History of requests
            limits: Rate limits (rpm, rph, rpd)
            current_time: Current timestamp
            
        Returns:
            Tuple of (exceeded: bool, requests_remaining: int)
        """
        requests = request_history.get(identifier, [])
        
        # Clean old requests (outside all windows)
        one_day_ago = current_time - 86400  # 24 hours
        requests = [r for r in requests if r > one_day_ago]
        request_history[identifier] = requests
        
        # Check per-minute limit
        one_minute_ago = current_time - 60
        rpm_count = len([r for r in requests if r > one_minute_ago])
        if rpm_count >= limits.get("rpm", float('inf')):
            return True, 0
        
        # Check per-hour limit
        one_hour_ago = current_time - 3600
        rph_count = len([r for r in requests if r > one_hour_ago])
        if rph_count >= limits.get("rph", float('inf')):
            return True, 0
        
        # Check per-day limit
        rpd_count = len(requests)
        if rpd_count >= limits.get("rpd", float('inf')):
            return True, 0
        
        # Calculate remaining requests (minimum across all windows)
        rpm_remaining = max(0, limits.get("rpm", 0) - rpm_count)
        rph_remaining = max(0, limits.get("rph", 0) - rph_count)
        rpd_remaining = max(0, limits.get("rpd", 0) - rpd_count)
        
        return False, min(rpm_remaining, rph_remaining, rpd_remaining)
    
    def _check_burst(self, identifier: str, current_time: float) -> bool:
        """
        Check burst protection (rapid requests in short window).
        
        Args:
            identifier: User/IP/Session identifier
            current_time: Current timestamp
            
        Returns:
            True if burst limit exceeded
        """
        window_start = current_time - (self.config.burst_window_ms / 1000.0)
        burst_window = self.burst_windows[identifier]
        
        # Clean old requests
        burst_window = [t for t in burst_window if t > window_start]
        self.burst_windows[identifier] = burst_window
        
        # Check burst limit
        if len(burst_window) >= self.config.burst_max_requests:
            return True
        
        # Record this request
        burst_window.append(current_time)
        self.burst_windows[identifier] = burst_window
        
        return False
    
    def reset_limits(self, identifier: str, limit_type: str = "all"):
        """
        Reset rate limits for an identifier (for testing/admin).
        
        Args:
            identifier: User/IP/Session identifier
            limit_type: Type of limit to reset (user, ip, session, all)
        """
        if limit_type in ["user", "all"]:
            self.user_requests.pop(identifier, None)
        if limit_type in ["ip", "all"]:
            self.ip_requests.pop(identifier, None)
        if limit_type in ["session", "all"]:
            self.session_requests.pop(identifier, None)
        
        self.burst_windows.pop(identifier, None)

