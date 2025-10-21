"""
Base storage interface for secure data persistence.

Defines the standard interface for all storage operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum


class StorageStatus(Enum):
    """Storage operation status."""
    SUCCESS = "success"
    FAILED = "failed"
    NOT_FOUND = "not_found"
    ENCRYPTION_ERROR = "encryption_error"
    PERMISSION_DENIED = "permission_denied"


@dataclass
class StorageResult:
    """Result of a storage operation."""
    status: StorageStatus
    message: str
    data: Optional[Dict[str, Any]] = None


class BaseStorage(ABC):
    """
    Abstract base class for all storage operations.
    
    Provides standardized interface for:
    - Secure credential storage
    - Metadata persistence
    - Encryption/decryption
    - Access control
    """
    
    @abstractmethod
    async def store_credentials(
        self, 
        user_id: str, 
        provider: str, 
        credentials: Dict[str, Any]
    ) -> StorageResult:
        """
        Store encrypted credentials for a user and provider.
        
        Args:
            user_id: User identifier
            provider: Model provider (e.g., 'openai')
            credentials: Credential data to encrypt and store
            
        Returns:
            StorageResult with operation status
        """
        pass
    
    @abstractmethod
    async def get_credentials(
        self, 
        user_id: str, 
        provider: str
    ) -> StorageResult:
        """
        Retrieve and decrypt credentials.
        
        Args:
            user_id: User identifier
            provider: Model provider
            
        Returns:
            StorageResult with decrypted credentials
        """
        pass
    
    @abstractmethod
    async def delete_credentials(
        self, 
        user_id: str, 
        provider: str
    ) -> StorageResult:
        """
        Delete stored credentials.
        
        Args:
            user_id: User identifier
            provider: Model provider
            
        Returns:
            StorageResult with operation status
        """
        pass
    
    @abstractmethod
    async def store_metadata(
        self, 
        model_id: str, 
        metadata: Dict[str, Any]
    ) -> StorageResult:
        """
        Store model metadata.
        
        Args:
            model_id: Unique model identifier
            metadata: Model metadata to store
            
        Returns:
            StorageResult with operation status
        """
        pass
    
    @abstractmethod
    async def get_metadata(
        self, 
        model_id: str
    ) -> StorageResult:
        """
        Retrieve model metadata.
        
        Args:
            model_id: Model identifier
            
        Returns:
            StorageResult with metadata
        """
        pass
    
    @abstractmethod
    async def list_user_models(
        self, 
        user_id: str
    ) -> StorageResult:
        """
        List all models for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            StorageResult with list of models
        """
        pass

