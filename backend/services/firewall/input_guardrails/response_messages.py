"""
Static response messages for different threat types.

These messages are returned to users when threats are detected.
All messages are neutral, professional, and don't reveal detection details.
"""


class ResponseMessages:
    """Static response messages for threat detection."""
    
    # Prompt Injection / Jailbreak responses
    PROMPT_INJECTION_BLOCKED = "I cannot help with that request. Please rephrase your question."
    JAILBREAK_BLOCKED = "I cannot help with that request. Please rephrase your question."
    
    # Harmful Content responses
    HARMFUL_CONTENT_VIOLENCE = "I cannot help with that. Please ask something else."
    HARMFUL_CONTENT_ILLEGAL = "I cannot help with that. Please ask something else."
    HARMFUL_CONTENT_HATE_SPEECH = "I cannot help with that. Please ask something else."
    HARMFUL_CONTENT_SELF_HARM = "I cannot help with that. Please ask something else."
    HARMFUL_CONTENT_EXPLICIT = "I cannot help with that. Please ask something else."
    HARMFUL_CONTENT_GENERIC = "I cannot help with that. Please ask something else."
    
    # PII responses
    PII_BLOCKED = "I cannot process messages containing sensitive personal information. Please remove any personal details and try again."
    PII_SANITIZED = "Your message has been processed with sensitive information removed for your protection."
    
    # Rate Limiting responses
    RATE_LIMIT_EXCEEDED = "Too many requests. Please wait a moment before trying again."
    
    # Generic blocked response
    GENERIC_BLOCKED = "I cannot help with that request. Please rephrase your question."
    
    @staticmethod
    def get_message_for_threat(threat_type: str, severity: str = "medium") -> str:
        """
        Get appropriate response message for a threat type.
        
        Args:
            threat_type: Type of threat detected
            severity: Severity level of the threat
            
        Returns:
            Static response message
        """
        threat_lower = threat_type.lower()
        
        if "prompt_injection" in threat_lower or "jailbreak" in threat_lower:
            return ResponseMessages.PROMPT_INJECTION_BLOCKED
        
        elif "harmful_content" in threat_lower:
            # Could be more specific based on content category
            return ResponseMessages.HARMFUL_CONTENT_GENERIC
        
        elif "pii" in threat_lower:
            return ResponseMessages.PII_BLOCKED
        
        elif "rate_limit" in threat_lower:
            return ResponseMessages.RATE_LIMIT_EXCEEDED
        
        else:
            return ResponseMessages.GENERIC_BLOCKED
    
    @staticmethod
    def get_message_for_harmful_content(category: str) -> str:
        """
        Get specific message for harmful content category.
        
        Args:
            category: Category of harmful content (violence, illegal, hate_speech, etc.)
            
        Returns:
            Specific response message
        """
        category_lower = category.lower()
        
        if "violence" in category_lower or "bomb" in category_lower or "weapon" in category_lower:
            return ResponseMessages.HARMFUL_CONTENT_VIOLENCE
        elif "illegal" in category_lower or "drug" in category_lower:
            return ResponseMessages.HARMFUL_CONTENT_ILLEGAL
        elif "hate" in category_lower or "discrimination" in category_lower:
            return ResponseMessages.HARMFUL_CONTENT_HATE_SPEECH
        elif "self_harm" in category_lower or "suicide" in category_lower:
            return ResponseMessages.HARMFUL_CONTENT_SELF_HARM
        elif "explicit" in category_lower or "sexual" in category_lower:
            return ResponseMessages.HARMFUL_CONTENT_EXPLICIT
        else:
            return ResponseMessages.HARMFUL_CONTENT_GENERIC

