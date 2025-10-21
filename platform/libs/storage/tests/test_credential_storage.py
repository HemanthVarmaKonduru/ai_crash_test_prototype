"""
Unit tests for credential storage with encryption.

Tests secure credential storage, encryption/decryption, and error handling.
"""

import pytest
import json
from unittest.mock import patch, Mock
from cryptography.fernet import Fernet
from src.credential_storage import CredentialStorage
from src.base import StorageStatus


class TestCredentialStorage:
    """Test CredentialStorage functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        # Generate a test encryption key
        self.encryption_key = Fernet.generate_key().decode()
        self.storage = CredentialStorage(self.encryption_key)
    
    def test_initialization(self):
        """Test CredentialStorage initialization."""
        assert self.storage.fernet is not None
        assert isinstance(self.storage._storage, dict)
    
    def test_get_storage_key(self):
        """Test storage key generation."""
        key = self.storage._get_storage_key("user123", "openai")
        assert key == "credentials:user123:openai"
    
    @pytest.mark.asyncio
    async def test_store_credentials_success(self):
        """Test successful credential storage."""
        credentials = {
            "api_key": "sk-test123",
            "model": "gpt-3.5-turbo",
            "provider": "openai"
        }
        
        result = await self.storage.store_credentials(
            user_id="user123",
            provider="openai",
            credentials=credentials
        )
        
        assert result.status == StorageStatus.SUCCESS
        assert "stored successfully" in result.message
        
        # Verify credentials are stored and encrypted
        storage_key = self.storage._get_storage_key("user123", "openai")
        assert storage_key in self.storage._storage
        
        stored_data = self.storage._storage[storage_key]
        assert "encrypted_credentials" in stored_data
        assert stored_data["provider"] == "openai"
        assert stored_data["user_id"] == "user123"
    
    @pytest.mark.asyncio
    async def test_store_credentials_encryption(self):
        """Test that credentials are properly encrypted."""
        credentials = {
            "api_key": "sk-secret-key",
            "model": "gpt-3.5-turbo"
        }
        
        await self.storage.store_credentials(
            user_id="user123",
            provider="openai",
            credentials=credentials
        )
        
        # Get stored encrypted data
        storage_key = self.storage._get_storage_key("user123", "openai")
        encrypted_data = self.storage._storage[storage_key]["encrypted_credentials"]
        
        # Verify it's encrypted (not plain text)
        assert "sk-secret-key" not in encrypted_data
        assert isinstance(encrypted_data, str)
        
        # Verify it can be decrypted
        decrypted_json = self.storage.fernet.decrypt(encrypted_data.encode())
        decrypted_credentials = json.loads(decrypted_json.decode())
        assert decrypted_credentials == credentials
    
    @pytest.mark.asyncio
    async def test_get_credentials_success(self):
        """Test successful credential retrieval."""
        # First store credentials
        credentials = {
            "api_key": "sk-test123",
            "model": "gpt-3.5-turbo"
        }
        
        await self.storage.store_credentials(
            user_id="user123",
            provider="openai",
            credentials=credentials
        )
        
        # Then retrieve them
        result = await self.storage.get_credentials(
            user_id="user123",
            provider="openai"
        )
        
        assert result.status == StorageStatus.SUCCESS
        assert "retrieved successfully" in result.message
        assert result.data == credentials
    
    @pytest.mark.asyncio
    async def test_get_credentials_not_found(self):
        """Test credential retrieval when credentials don't exist."""
        result = await self.storage.get_credentials(
            user_id="nonexistent",
            provider="openai"
        )
        
        assert result.status == StorageStatus.NOT_FOUND
        assert "not found" in result.message
    
    @pytest.mark.asyncio
    async def test_delete_credentials_success(self):
        """Test successful credential deletion."""
        # First store credentials
        credentials = {"api_key": "sk-test123"}
        await self.storage.store_credentials(
            user_id="user123",
            provider="openai",
            credentials=credentials
        )
        
        # Verify they exist
        storage_key = self.storage._get_storage_key("user123", "openai")
        assert storage_key in self.storage._storage
        
        # Delete them
        result = await self.storage.delete_credentials(
            user_id="user123",
            provider="openai"
        )
        
        assert result.status == StorageStatus.SUCCESS
        assert "deleted successfully" in result.message
        assert storage_key not in self.storage._storage
    
    @pytest.mark.asyncio
    async def test_delete_credentials_not_found(self):
        """Test credential deletion when credentials don't exist."""
        result = await self.storage.delete_credentials(
            user_id="nonexistent",
            provider="openai"
        )
        
        assert result.status == StorageStatus.NOT_FOUND
        assert "not found" in result.message
    
    @pytest.mark.asyncio
    async def test_store_credentials_encryption_error(self):
        """Test credential storage with encryption error."""
        # Create storage with invalid encryption key (not base64 encoded)
        with pytest.raises(ValueError, match="Fernet key must be 32 url-safe base64-encoded bytes"):
            CredentialStorage("invalid-key")
    
    @pytest.mark.asyncio
    async def test_get_credentials_decryption_error(self):
        """Test credential retrieval with decryption error."""
        # Store credentials normally
        credentials = {"api_key": "sk-test123"}
        await self.storage.store_credentials(
            user_id="user123",
            provider="openai",
            credentials=credentials
        )
        
        # Corrupt the encrypted data
        storage_key = self.storage._get_storage_key("user123", "openai")
        self.storage._storage[storage_key]["encrypted_credentials"] = "corrupted-data"
        
        result = await self.storage.get_credentials(
            user_id="user123",
            provider="openai"
        )
        
        assert result.status == StorageStatus.FAILED
        assert "Failed to retrieve credentials" in result.message
    
    @pytest.mark.asyncio
    async def test_metadata_operations_delegation(self):
        """Test that metadata operations are properly delegated."""
        # Test store_metadata delegation
        result = await self.storage.store_metadata("model123", {"key": "value"})
        assert result.status == StorageStatus.FAILED
        assert "Use ModelMetadataStorage" in result.message
        
        # Test get_metadata delegation
        result = await self.storage.get_metadata("model123")
        assert result.status == StorageStatus.FAILED
        assert "Use ModelMetadataStorage" in result.message
        
        # Test list_user_models delegation
        result = await self.storage.list_user_models("user123")
        assert result.status == StorageStatus.FAILED
        assert "Use ModelMetadataStorage" in result.message
    
    @pytest.mark.asyncio
    async def test_multiple_users_providers(self):
        """Test storage with multiple users and providers."""
        # Store credentials for different users and providers
        await self.storage.store_credentials(
            user_id="user1",
            provider="openai",
            credentials={"api_key": "sk-user1-openai"}
        )
        
        await self.storage.store_credentials(
            user_id="user1",
            provider="anthropic",
            credentials={"api_key": "ant-user1-anthropic"}
        )
        
        await self.storage.store_credentials(
            user_id="user2",
            provider="openai",
            credentials={"api_key": "sk-user2-openai"}
        )
        
        # Verify all are stored separately
        assert len(self.storage._storage) == 3
        
        # Verify retrieval works for each
        result1 = await self.storage.get_credentials("user1", "openai")
        assert result1.data["api_key"] == "sk-user1-openai"
        
        result2 = await self.storage.get_credentials("user1", "anthropic")
        assert result2.data["api_key"] == "ant-user1-anthropic"
        
        result3 = await self.storage.get_credentials("user2", "openai")
        assert result3.data["api_key"] == "sk-user2-openai"
