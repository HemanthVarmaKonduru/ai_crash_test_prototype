"""
Unit tests for model metadata storage.

Tests metadata persistence, user model listing, and error handling.
"""

import pytest
from datetime import datetime
from src.model_metadata import ModelMetadataStorage
from src.base import StorageStatus


class TestModelMetadataStorage:
    """Test ModelMetadataStorage functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.storage = ModelMetadataStorage()
    
    def test_initialization(self):
        """Test ModelMetadataStorage initialization."""
        assert isinstance(self.storage._metadata_storage, dict)
        assert isinstance(self.storage._user_models, dict)
    
    @pytest.mark.asyncio
    async def test_store_metadata_success(self):
        """Test successful metadata storage."""
        metadata = {
            "model_id": "user123:openai:gpt-3.5-turbo",
            "user_id": "user123",
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "status": "connected",
            "latency_ms": 245.5
        }
        
        result = await self.storage.store_metadata(
            model_id="user123:openai:gpt-3.5-turbo",
            metadata=metadata
        )
        
        assert result.status == StorageStatus.SUCCESS
        assert "stored successfully" in result.message
        
        # Verify metadata is stored
        assert "user123:openai:gpt-3.5-turbo" in self.storage._metadata_storage
        stored_metadata = self.storage._metadata_storage["user123:openai:gpt-3.5-turbo"]
        assert stored_metadata["user_id"] == "user123"
        assert stored_metadata["provider"] == "openai"
        assert "updated_at" in stored_metadata
    
    @pytest.mark.asyncio
    async def test_store_metadata_timestamp(self):
        """Test that metadata gets timestamp when stored."""
        metadata = {
            "model_id": "test-model",
            "user_id": "user123",
            "provider": "openai"
        }
        
        await self.storage.store_metadata("test-model", metadata)
        
        stored_metadata = self.storage._metadata_storage["test-model"]
        assert "updated_at" in stored_metadata
        # Verify it's a valid ISO timestamp
        datetime.fromisoformat(stored_metadata["updated_at"].replace("Z", "+00:00"))
    
    @pytest.mark.asyncio
    async def test_store_metadata_user_tracking(self):
        """Test that user model tracking works."""
        metadata = {
            "model_id": "user123:openai:gpt-3.5-turbo",
            "user_id": "user123",
            "provider": "openai"
        }
        
        await self.storage.store_metadata("user123:openai:gpt-3.5-turbo", metadata)
        
        # Verify user is tracked
        assert "user123" in self.storage._user_models
        assert "user123:openai:gpt-3.5-turbo" in self.storage._user_models["user123"]
    
    @pytest.mark.asyncio
    async def test_get_metadata_success(self):
        """Test successful metadata retrieval."""
        # First store metadata
        metadata = {
            "model_id": "test-model",
            "user_id": "user123",
            "provider": "openai",
            "status": "connected"
        }
        
        await self.storage.store_metadata("test-model", metadata)
        
        # Then retrieve it
        result = await self.storage.get_metadata("test-model")
        
        assert result.status == StorageStatus.SUCCESS
        assert "retrieved successfully" in result.message
        assert result.data["user_id"] == "user123"
        assert result.data["provider"] == "openai"
        assert result.data["status"] == "connected"
    
    @pytest.mark.asyncio
    async def test_get_metadata_not_found(self):
        """Test metadata retrieval when metadata doesn't exist."""
        result = await self.storage.get_metadata("nonexistent-model")
        
        assert result.status == StorageStatus.NOT_FOUND
        assert "not found" in result.message
    
    @pytest.mark.asyncio
    async def test_list_user_models_success(self):
        """Test successful user model listing."""
        # Store multiple models for a user
        metadata1 = {
            "model_id": "user123:openai:gpt-3.5-turbo",
            "user_id": "user123",
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "name": "GPT-3.5 Model"
        }
        
        metadata2 = {
            "model_id": "user123:openai:gpt-4",
            "user_id": "user123",
            "provider": "openai",
            "model": "gpt-4",
            "name": "GPT-4 Model"
        }
        
        await self.storage.store_metadata("user123:openai:gpt-3.5-turbo", metadata1)
        await self.storage.store_metadata("user123:openai:gpt-4", metadata2)
        
        # List user models
        result = await self.storage.list_user_models("user123")
        
        assert result.status == StorageStatus.SUCCESS
        assert "Found 2 models" in result.message
        assert len(result.data["models"]) == 2
        
        # Verify both models are included
        model_ids = [model["model_id"] for model in result.data["models"]]
        assert "user123:openai:gpt-3.5-turbo" in model_ids
        assert "user123:openai:gpt-4" in model_ids
    
    @pytest.mark.asyncio
    async def test_list_user_models_empty(self):
        """Test user model listing when user has no models."""
        result = await self.storage.list_user_models("nonexistent-user")
        
        assert result.status == StorageStatus.SUCCESS
        assert "Found 0 models" in result.message
        assert result.data["models"] == []
    
    @pytest.mark.asyncio
    async def test_list_user_models_with_missing_metadata(self):
        """Test user model listing when some metadata is missing."""
        # Add user to tracking but don't store metadata
        self.storage._user_models["user123"] = ["missing-model"]
        
        result = await self.storage.list_user_models("user123")
        
        assert result.status == StorageStatus.SUCCESS
        assert "Found 0 models" in result.message
        assert result.data["models"] == []
    
    @pytest.mark.asyncio
    async def test_store_metadata_error_handling(self):
        """Test metadata storage error handling."""
        # Mock an error during storage
        from unittest.mock import Mock
        mock_storage = Mock()
        mock_storage.__setitem__ = Mock(side_effect=Exception("Storage error"))
        self.storage._metadata_storage = mock_storage
        
        result = await self.storage.store_metadata("test-model", {"key": "value"})
        
        assert result.status == StorageStatus.FAILED
        assert "Failed to store metadata" in result.message
    
    @pytest.mark.asyncio
    async def test_get_metadata_error_handling(self):
        """Test metadata retrieval error handling."""
        # Mock an error during retrieval
        from unittest.mock import Mock
        mock_storage = Mock()
        mock_storage.__getitem__ = Mock(side_effect=Exception("Retrieval error"))
        self.storage._metadata_storage = mock_storage
        
        result = await self.storage.get_metadata("test-model")
        
        assert result.status == StorageStatus.FAILED
        assert "Failed to retrieve metadata" in result.message
    
    @pytest.mark.asyncio
    async def test_list_user_models_error_handling(self):
        """Test user model listing error handling."""
        # Mock an error during listing
        from unittest.mock import Mock
        mock_user_models = Mock()
        mock_user_models.get = Mock(side_effect=Exception("Listing error"))
        self.storage._user_models = mock_user_models
        
        result = await self.storage.list_user_models("user123")
        
        assert result.status == StorageStatus.FAILED
        assert "Failed to list user models" in result.message
    
    @pytest.mark.asyncio
    async def test_credential_operations_delegation(self):
        """Test that credential operations are properly delegated."""
        # Test store_credentials delegation
        result = await self.storage.store_credentials("user123", "openai", {"key": "value"})
        assert result.status == StorageStatus.FAILED
        assert "Use CredentialStorage" in result.message
        
        # Test get_credentials delegation
        result = await self.storage.get_credentials("user123", "openai")
        assert result.status == StorageStatus.FAILED
        assert "Use CredentialStorage" in result.message
        
        # Test delete_credentials delegation
        result = await self.storage.delete_credentials("user123", "openai")
        assert result.status == StorageStatus.FAILED
        assert "Use CredentialStorage" in result.message
    
    @pytest.mark.asyncio
    async def test_multiple_users_isolation(self):
        """Test that different users' models are properly isolated."""
        # Store models for different users
        await self.storage.store_metadata("user1:openai:gpt-3.5", {
            "model_id": "user1:openai:gpt-3.5",
            "user_id": "user1",
            "provider": "openai"
        })
        
        await self.storage.store_metadata("user2:openai:gpt-4", {
            "model_id": "user2:openai:gpt-4",
            "user_id": "user2",
            "provider": "openai"
        })
        
        # List models for each user
        user1_result = await self.storage.list_user_models("user1")
        user2_result = await self.storage.list_user_models("user2")
        
        assert len(user1_result.data["models"]) == 1
        assert len(user2_result.data["models"]) == 1
        assert user1_result.data["models"][0]["user_id"] == "user1"
        assert user2_result.data["models"][0]["user_id"] == "user2"
