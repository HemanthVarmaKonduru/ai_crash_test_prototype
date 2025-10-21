"""
Unit tests for custom error classes.

Tests error hierarchy, inheritance, and error handling.
"""

import pytest
from src.errors import (
    AdversarialSandboxError, ValidationError, ConnectionError,
    AuthenticationError, StorageError, ModelError
)


class TestAdversarialSandboxError:
    """Test base AdversarialSandboxError class."""
    
    def test_base_error_creation(self):
        """Test base error creation with message only."""
        error = AdversarialSandboxError("Test error message")
        
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.error_code is None
    
    def test_base_error_creation_with_code(self):
        """Test base error creation with message and error code."""
        error = AdversarialSandboxError("Test error message", "TEST_ERROR")
        
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.error_code == "TEST_ERROR"
    
    def test_base_error_inheritance(self):
        """Test that base error inherits from Exception."""
        error = AdversarialSandboxError("Test error")
        
        assert isinstance(error, Exception)
        assert isinstance(error, AdversarialSandboxError)


class TestValidationError:
    """Test ValidationError class."""
    
    def test_validation_error_creation(self):
        """Test ValidationError creation with message only."""
        error = ValidationError("Invalid input")
        
        assert str(error) == "Invalid input"
        assert error.message == "Invalid input"
        assert error.error_code == "VALIDATION_ERROR"
        assert error.field is None
    
    def test_validation_error_creation_with_field(self):
        """Test ValidationError creation with field."""
        error = ValidationError("Invalid email format", "email")
        
        assert str(error) == "Invalid email format"
        assert error.message == "Invalid email format"
        assert error.error_code == "VALIDATION_ERROR"
        assert error.field == "email"
    
    def test_validation_error_inheritance(self):
        """Test ValidationError inheritance."""
        error = ValidationError("Invalid input")
        
        assert isinstance(error, Exception)
        assert isinstance(error, AdversarialSandboxError)
        assert isinstance(error, ValidationError)


class TestConnectionError:
    """Test ConnectionError class."""
    
    def test_connection_error_creation(self):
        """Test ConnectionError creation with message only."""
        error = ConnectionError("Connection failed")
        
        assert str(error) == "Connection failed"
        assert error.message == "Connection failed"
        assert error.error_code == "CONNECTION_ERROR"
        assert error.service is None
    
    def test_connection_error_creation_with_service(self):
        """Test ConnectionError creation with service."""
        error = ConnectionError("Database connection failed", "database")
        
        assert str(error) == "Database connection failed"
        assert error.message == "Database connection failed"
        assert error.error_code == "CONNECTION_ERROR"
        assert error.service == "database"
    
    def test_connection_error_inheritance(self):
        """Test ConnectionError inheritance."""
        error = ConnectionError("Connection failed")
        
        assert isinstance(error, Exception)
        assert isinstance(error, AdversarialSandboxError)
        assert isinstance(error, ConnectionError)


class TestAuthenticationError:
    """Test AuthenticationError class."""
    
    def test_authentication_error_creation_default(self):
        """Test AuthenticationError creation with default message."""
        error = AuthenticationError()
        
        assert str(error) == "Authentication failed"
        assert error.message == "Authentication failed"
        assert error.error_code == "AUTHENTICATION_ERROR"
    
    def test_authentication_error_creation_custom(self):
        """Test AuthenticationError creation with custom message."""
        error = AuthenticationError("Invalid token")
        
        assert str(error) == "Invalid token"
        assert error.message == "Invalid token"
        assert error.error_code == "AUTHENTICATION_ERROR"
    
    def test_authentication_error_inheritance(self):
        """Test AuthenticationError inheritance."""
        error = AuthenticationError()
        
        assert isinstance(error, Exception)
        assert isinstance(error, AdversarialSandboxError)
        assert isinstance(error, AuthenticationError)


class TestStorageError:
    """Test StorageError class."""
    
    def test_storage_error_creation(self):
        """Test StorageError creation with message only."""
        error = StorageError("Storage operation failed")
        
        assert str(error) == "Storage operation failed"
        assert error.message == "Storage operation failed"
        assert error.error_code == "STORAGE_ERROR"
        assert error.operation is None
    
    def test_storage_error_creation_with_operation(self):
        """Test StorageError creation with operation."""
        error = StorageError("Failed to write data", "write")
        
        assert str(error) == "Failed to write data"
        assert error.message == "Failed to write data"
        assert error.error_code == "STORAGE_ERROR"
        assert error.operation == "write"
    
    def test_storage_error_inheritance(self):
        """Test StorageError inheritance."""
        error = StorageError("Storage failed")
        
        assert isinstance(error, Exception)
        assert isinstance(error, AdversarialSandboxError)
        assert isinstance(error, StorageError)


class TestModelError:
    """Test ModelError class."""
    
    def test_model_error_creation(self):
        """Test ModelError creation with message only."""
        error = ModelError("Model operation failed")
        
        assert str(error) == "Model operation failed"
        assert error.message == "Model operation failed"
        assert error.error_code == "MODEL_ERROR"
        assert error.model_id is None
    
    def test_model_error_creation_with_model_id(self):
        """Test ModelError creation with model ID."""
        error = ModelError("Model inference failed", "model-123")
        
        assert str(error) == "Model inference failed"
        assert error.message == "Model inference failed"
        assert error.error_code == "MODEL_ERROR"
        assert error.model_id == "model-123"
    
    def test_model_error_inheritance(self):
        """Test ModelError inheritance."""
        error = ModelError("Model failed")
        
        assert isinstance(error, Exception)
        assert isinstance(error, AdversarialSandboxError)
        assert isinstance(error, ModelError)


class TestErrorHierarchy:
    """Test error hierarchy and relationships."""
    
    def test_error_hierarchy(self):
        """Test that all custom errors inherit from base error."""
        errors = [
            ValidationError("test"),
            ConnectionError("test"),
            AuthenticationError("test"),
            StorageError("test"),
            ModelError("test")
        ]
        
        for error in errors:
            assert isinstance(error, AdversarialSandboxError)
            assert isinstance(error, Exception)
    
    def test_error_catching(self):
        """Test error catching with different error types."""
        # Test catching specific error types
        try:
            raise ValidationError("Invalid input", "email")
        except ValidationError as e:
            assert e.field == "email"
        except AdversarialSandboxError:
            pytest.fail("Should have caught ValidationError specifically")
        
        # Test catching base error type
        try:
            raise ConnectionError("Connection failed", "database")
        except AdversarialSandboxError as e:
            assert e.error_code == "CONNECTION_ERROR"
            assert e.service == "database"
    
    def test_error_attributes(self):
        """Test that all error attributes are accessible."""
        error = ValidationError("Test message", "test_field")
        
        assert hasattr(error, 'message')
        assert hasattr(error, 'error_code')
        assert hasattr(error, 'field')
        
        error = ConnectionError("Test message", "test_service")
        
        assert hasattr(error, 'message')
        assert hasattr(error, 'error_code')
        assert hasattr(error, 'service')
        
        error = StorageError("Test message", "test_operation")
        
        assert hasattr(error, 'message')
        assert hasattr(error, 'error_code')
        assert hasattr(error, 'operation')
        
        error = ModelError("Test message", "test_model")
        
        assert hasattr(error, 'message')
        assert hasattr(error, 'error_code')
        assert hasattr(error, 'model_id')

