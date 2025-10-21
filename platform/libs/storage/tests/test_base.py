"""
Unit tests for base storage interface.

Tests the abstract base class and data structures.
"""

import pytest
from src.base import BaseStorage, StorageResult, StorageStatus


class TestStorageResult:
    """Test StorageResult dataclass."""
    
    def test_storage_result_creation(self):
        """Test StorageResult creation with all fields."""
        result = StorageResult(
            status=StorageStatus.SUCCESS,
            message="Operation successful",
            data={"key": "value"}
        )
        
        assert result.status == StorageStatus.SUCCESS
        assert result.message == "Operation successful"
        assert result.data == {"key": "value"}
    
    def test_storage_result_minimal(self):
        """Test StorageResult creation with minimal fields."""
        result = StorageResult(
            status=StorageStatus.FAILED,
            message="Operation failed"
        )
        
        assert result.status == StorageStatus.FAILED
        assert result.message == "Operation failed"
        assert result.data is None


class TestStorageStatus:
    """Test StorageStatus enum."""
    
    def test_storage_status_values(self):
        """Test StorageStatus enum values."""
        assert StorageStatus.SUCCESS.value == "success"
        assert StorageStatus.FAILED.value == "failed"
        assert StorageStatus.NOT_FOUND.value == "not_found"
        assert StorageStatus.ENCRYPTION_ERROR.value == "encryption_error"
        assert StorageStatus.PERMISSION_DENIED.value == "permission_denied"


class TestBaseStorage:
    """Test BaseStorage abstract class."""
    
    def test_base_storage_abstract_methods(self):
        """Test that BaseStorage cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseStorage()
    
    def test_base_storage_must_implement_methods(self):
        """Test that concrete classes must implement all abstract methods."""
        class IncompleteStorage(BaseStorage):
            pass
        
        with pytest.raises(TypeError):
            IncompleteStorage()

