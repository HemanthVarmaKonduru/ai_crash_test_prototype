"""
Credential storage implementation.

Handles secure storage and encryption of API credentials.
"""

import json
import hashlib
from typing import Dict, Any
from cryptography.fernet import Fernet
from .base import BaseStorage, StorageResult, StorageStatus


class CredentialStorage(BaseStorage):
    """
    Secure credential storage with encryption.
    
    Stores encrypted API keys and credentials for different providers.
    """
    
    def __init__(self, encryption_key: str):
        """
        Initialize credential storage.
        
        Args:
            encryption_key: Base64-encoded encryption key
        """
        self.fernet = Fernet(encryption_key.encode())
        # In production, this would connect to a real database
        self._storage = {}
    
    def _get_storage_key(self, user_id: str, provider: str) -> str:
        """Generate storage key for user-provider combination."""
        return f"credentials:{user_id}:{provider}"
    
    async def store_credentials(
        self, 
        user_id: str, 
        provider: str, 
        credentials: Dict[str, Any]
    ) -> StorageResult:
        """
        Store encrypted credentials.
        
        Args:
            user_id: User identifier
            provider: Model provider
            credentials: Credential data to encrypt
            
        Returns:
            StorageResult with operation status
        """
        try:
            # Serialize credentials
            credentials_json = json.dumps(credentials)
            
            # Encrypt credentials
            encrypted_data = self.fernet.encrypt(credentials_json.encode())
            
            # Store with metadata
            storage_key = self._get_storage_key(user_id, provider)
            self._storage[storage_key] = {
                "encrypted_credentials": encrypted_data.decode(),
                "provider": provider,
                "user_id": user_id,
                "created_at": "2025-01-01T00:00:00Z"  # In production, use actual timestamp
            }
            
            return StorageResult(
                status=StorageStatus.SUCCESS,
                message="Credentials stored successfully"
            )
            
        except Exception as e:
            return StorageResult(
                status=StorageStatus.ENCRYPTION_ERROR,
                message=f"Failed to store credentials: {str(e)}"
            )
    
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
        try:
            storage_key = self._get_storage_key(user_id, provider)
            
            if storage_key not in self._storage:
                return StorageResult(
                    status=StorageStatus.NOT_FOUND,
                    message="Credentials not found"
                )
            
            # Get encrypted data
            encrypted_data = self._storage[storage_key]["encrypted_credentials"]
            
            # Decrypt credentials
            decrypted_json = self.fernet.decrypt(encrypted_data.encode())
            credentials = json.loads(decrypted_json.decode())
            
            return StorageResult(
                status=StorageStatus.SUCCESS,
                message="Credentials retrieved successfully",
                data=credentials
            )
            
        except Exception as e:
            return StorageResult(
                status=StorageStatus.FAILED,
                message=f"Failed to retrieve credentials: {str(e)}"
            )
    
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
        try:
            storage_key = self._get_storage_key(user_id, provider)
            
            if storage_key not in self._storage:
                return StorageResult(
                    status=StorageStatus.NOT_FOUND,
                    message="Credentials not found"
                )
            
            # Delete credentials
            del self._storage[storage_key]
            
            return StorageResult(
                status=StorageStatus.SUCCESS,
                message="Credentials deleted successfully"
            )
            
        except Exception as e:
            return StorageResult(
                status=StorageStatus.FAILED,
                message=f"Failed to delete credentials: {str(e)}"
            )
    
    async def store_metadata(
        self, 
        model_id: str, 
        metadata: Dict[str, Any]
    ) -> StorageResult:
        """Store model metadata (delegated to ModelMetadataStorage)."""
        return StorageResult(
            status=StorageStatus.FAILED,
            message="Use ModelMetadataStorage for metadata operations"
        )
    
    async def get_metadata(
        self, 
        model_id: str
    ) -> StorageResult:
        """Get model metadata (delegated to ModelMetadataStorage)."""
        return StorageResult(
            status=StorageStatus.FAILED,
            message="Use ModelMetadataStorage for metadata operations"
        )
    
    async def list_user_models(
        self, 
        user_id: str
    ) -> StorageResult:
        """List user models (delegated to ModelMetadataStorage)."""
        return StorageResult(
            status=StorageStatus.FAILED,
            message="Use ModelMetadataStorage for model listing"
        )

