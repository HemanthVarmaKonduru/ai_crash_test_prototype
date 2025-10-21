"""
Storage Library - Secure Data Persistence

This module provides interfaces for secure storage of credentials and metadata.
Handles encryption, database operations, and secure key management.
"""

from .base import BaseStorage, StorageResult
from .credential_storage import CredentialStorage
from .model_metadata import ModelMetadataStorage

__all__ = [
    "BaseStorage",
    "StorageResult",
    "CredentialStorage", 
    "ModelMetadataStorage"
]

