"""
Authentication service for user login/logout/verification.
"""
import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.config.settings import VALID_EMAIL, VALID_PASSWORD, SESSION_EXPIRY_HOURS

# In-memory session storage (in production, use Redis or database)
active_sessions: Dict[str, Dict[str, Any]] = {}

def validate_credentials(email: str, password: str) -> bool:
    """Validate user credentials."""
    return email == VALID_EMAIL and password == VALID_PASSWORD

def create_session(email: str) -> str:
    """Create a new session and return the token."""
    token = f"auth_{int(time.time())}_{str(uuid.uuid4())[:8]}"
    
    active_sessions[token] = {
        "email": email,
        "token": token,
        "created_at": datetime.now().isoformat(),
        "expires_at": datetime.now().timestamp() + (SESSION_EXPIRY_HOURS * 3600)
    }
    
    return token

def get_session(token: str) -> Optional[Dict[str, Any]]:
    """Get session by token."""
    return active_sessions.get(token)

def delete_session(token: str) -> bool:
    """Delete a session."""
    if token in active_sessions:
        del active_sessions[token]
        return True
    return False

def is_session_valid(token: str) -> bool:
    """Check if session is valid and not expired."""
    session = active_sessions.get(token)
    if not session:
        return False
    
    # Check expiration
    if datetime.now().timestamp() > session["expires_at"]:
        del active_sessions[token]
        return False
    
    return True

