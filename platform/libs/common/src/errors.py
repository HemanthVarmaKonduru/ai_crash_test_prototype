"""
Custom error classes for the Adversarial Sandbox platform.

Provides standardized error handling across all services.
"""


class AdversarialSandboxError(Exception):
    """Base exception for all Adversarial Sandbox errors."""
    
    def __init__(self, message: str, error_code: str = None):
        """
        Initialize base error.
        
        Args:
            message: Error message
            error_code: Optional error code
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ValidationError(AdversarialSandboxError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: str = None):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            field: Field that failed validation
        """
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field


class ConnectionError(AdversarialSandboxError):
    """Raised when connection to external service fails."""
    
    def __init__(self, message: str, service: str = None):
        """
        Initialize connection error.
        
        Args:
            message: Error message
            service: Service that failed to connect
        """
        super().__init__(message, "CONNECTION_ERROR")
        self.service = service


class AuthenticationError(AdversarialSandboxError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        """
        Initialize authentication error.
        
        Args:
            message: Error message
        """
        super().__init__(message, "AUTHENTICATION_ERROR")


class StorageError(AdversarialSandboxError):
    """Raised when storage operations fail."""
    
    def __init__(self, message: str, operation: str = None):
        """
        Initialize storage error.
        
        Args:
            message: Error message
            operation: Storage operation that failed
        """
        super().__init__(message, "STORAGE_ERROR")
        self.operation = operation


class ModelError(AdversarialSandboxError):
    """Raised when model operations fail."""
    
    def __init__(self, message: str, model_id: str = None):
        """
        Initialize model error.
        
        Args:
            message: Error message
            model_id: Model that caused the error
        """
        super().__init__(message, "MODEL_ERROR")
        self.model_id = model_id

