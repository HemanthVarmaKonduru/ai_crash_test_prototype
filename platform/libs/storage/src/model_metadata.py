"""
Model metadata storage implementation.

Handles persistence of model connection metadata and status.
"""

import json
from typing import Dict, Any, List
from datetime import datetime
from .base import BaseStorage, StorageResult, StorageStatus


class ModelMetadataStorage(BaseStorage):
    """
    Model metadata storage for connection status and model information.
    
    Stores model metadata including connection status, latency, and configuration.
    """
    
    def __init__(self):
        """Initialize model metadata storage."""
        # In production, this would connect to a real database
        self._metadata_storage = {}
        self._user_models = {}
    
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
        try:
            # Add timestamp
            metadata["updated_at"] = datetime.utcnow().isoformat()
            
            # Store metadata
            self._metadata_storage[model_id] = metadata
            
            # Update user's model list
            user_id = metadata.get("user_id")
            if user_id:
                if user_id not in self._user_models:
                    self._user_models[user_id] = []
                if model_id not in self._user_models[user_id]:
                    self._user_models[user_id].append(model_id)
            
            return StorageResult(
                status=StorageStatus.SUCCESS,
                message="Metadata stored successfully"
            )
            
        except Exception as e:
            return StorageResult(
                status=StorageStatus.FAILED,
                message=f"Failed to store metadata: {str(e)}"
            )
    
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
        try:
            if model_id not in self._metadata_storage:
                return StorageResult(
                    status=StorageStatus.NOT_FOUND,
                    message="Model metadata not found"
                )
            
            metadata = self._metadata_storage[model_id]
            
            return StorageResult(
                status=StorageStatus.SUCCESS,
                message="Metadata retrieved successfully",
                data=metadata
            )
            
        except Exception as e:
            return StorageResult(
                status=StorageStatus.FAILED,
                message=f"Failed to retrieve metadata: {str(e)}"
            )
    
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
        try:
            user_models = self._user_models.get(user_id, [])
            
            # Get metadata for each model
            models_data = []
            for model_id in user_models:
                if model_id in self._metadata_storage:
                    models_data.append(self._metadata_storage[model_id])
            
            return StorageResult(
                status=StorageStatus.SUCCESS,
                message=f"Found {len(models_data)} models for user",
                data={"models": models_data}
            )
            
        except Exception as e:
            return StorageResult(
                status=StorageStatus.FAILED,
                message=f"Failed to list user models: {str(e)}"
            )
    
    async def store_credentials(
        self, 
        user_id: str, 
        provider: str, 
        credentials: Dict[str, Any]
    ) -> StorageResult:
        """Store credentials (delegated to CredentialStorage)."""
        return StorageResult(
            status=StorageStatus.FAILED,
            message="Use CredentialStorage for credential operations"
        )
    
    async def get_credentials(
        self, 
        user_id: str, 
        provider: str
    ) -> StorageResult:
        """Get credentials (delegated to CredentialStorage)."""
        return StorageResult(
            status=StorageStatus.FAILED,
            message="Use CredentialStorage for credential operations"
        )
    
    async def delete_credentials(
        self, 
        user_id: str, 
        provider: str
    ) -> StorageResult:
        """Delete credentials (delegated to CredentialStorage)."""
        return StorageResult(
            status=StorageStatus.FAILED,
            message="Use CredentialStorage for credential operations"
        )

