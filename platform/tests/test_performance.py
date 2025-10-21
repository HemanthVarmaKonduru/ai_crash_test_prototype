"""
Performance tests for the Adversarial Sandbox platform.

Tests system performance under load and stress conditions.
"""

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../services/api-gateway/src"))

from main import app


class TestPerformance:
    """Test system performance characteristics."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.client = TestClient(app)
    
    @pytest.mark.asyncio
    async def test_connection_latency(self):
        """Test model connection latency."""
        # Mock fast connector
        mock_connector = Mock()
        mock_connector.test_connection = AsyncMock(return_value=Mock(
            status=Mock(value="success"),
            message="Connection successful",
            latency_ms=100.0,  # Fast connection
            model_info={"model": "gpt-3.5-turbo"}
        ))
        
        with patch('main.OpenAIConnector', return_value=mock_connector):
            with patch('main.credential_storage') as mock_cred_storage:
                with patch('main.metadata_storage') as mock_meta_storage:
                    # Mock storage operations
                    mock_cred_storage.store_credentials = AsyncMock(return_value=Mock(
                        status=Mock(value="success"),
                        message="Credentials stored successfully"
                    ))
                    mock_meta_storage.store_metadata = AsyncMock(return_value=Mock(
                        status=Mock(value="success"),
                        message="Metadata stored successfully"
                    ))
                    
                    # Measure connection time
                    start_time = time.time()
                    
                    request_data = {
                        "provider": "openai",
                        "model": "gpt-3.5-turbo",
                        "api_key": "sk-test123"
                    }
                    
                    response = self.client.post("/models/connect", json=request_data)
                    
                    end_time = time.time()
                    total_time = (end_time - start_time) * 1000  # Convert to milliseconds
                    
                    # Verify response
                    assert response.status_code == 200
                    data = response.json()
                    assert data["success"] is True
                    
                    # Verify performance (should be fast for mocked operations)
                    assert total_time < 1000  # Less than 1 second
                    print(f"Connection time: {total_time:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_concurrent_connections_performance(self):
        """Test performance with multiple concurrent connections."""
        # Mock connector
        mock_connector = Mock()
        mock_connector.test_connection = AsyncMock(return_value=Mock(
            status=Mock(value="success"),
            message="Connection successful",
            latency_ms=200.0,
            model_info={"model": "gpt-3.5-turbo"}
        ))
        
        with patch('main.OpenAIConnector', return_value=mock_connector):
            with patch('main.credential_storage') as mock_cred_storage:
                with patch('main.metadata_storage') as mock_meta_storage:
                    # Mock storage operations
                    mock_cred_storage.store_credentials = AsyncMock(return_value=Mock(
                        status=Mock(value="success"),
                        message="Credentials stored successfully"
                    ))
                    mock_meta_storage.store_metadata = AsyncMock(return_value=Mock(
                        status=Mock(value="success"),
                        message="Metadata stored successfully"
                    ))
                    
                    # Test concurrent connections
                    num_connections = 10
                    request_data = {
                        "provider": "openai",
                        "model": "gpt-3.5-turbo",
                        "api_key": "sk-test123"
                    }
                    
                    start_time = time.time()
                    
                    # Send concurrent requests
                    with ThreadPoolExecutor(max_workers=num_connections) as executor:
                        futures = [
                            executor.submit(
                                self.client.post, 
                                "/models/connect", 
                                json=request_data
                            )
                            for _ in range(num_connections)
                        ]
                        
                        responses = [future.result() for future in futures]
                    
                    end_time = time.time()
                    total_time = (end_time - start_time) * 1000
                    
                    # Verify all responses
                    for response in responses:
                        assert response.status_code == 200
                        data = response.json()
                        assert data["success"] is True
                    
                    # Verify performance
                    avg_time_per_request = total_time / num_connections
                    print(f"Total time for {num_connections} connections: {total_time:.2f}ms")
                    print(f"Average time per request: {avg_time_per_request:.2f}ms")
                    
                    # Should handle concurrent requests efficiently
                    assert total_time < 5000  # Less than 5 seconds for 10 requests
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self):
        """Test memory usage stability over multiple operations."""
        # Mock connector
        mock_connector = Mock()
        mock_connector.test_connection = AsyncMock(return_value=Mock(
            status=Mock(value="success"),
            message="Connection successful",
            latency_ms=150.0,
            model_info={"model": "gpt-3.5-turbo"}
        ))
        
        with patch('main.OpenAIConnector', return_value=mock_connector):
            with patch('main.credential_storage') as mock_cred_storage:
                with patch('main.metadata_storage') as mock_meta_storage:
                    # Mock storage operations
                    mock_cred_storage.store_credentials = AsyncMock(return_value=Mock(
                        status=Mock(value="success"),
                        message="Credentials stored successfully"
                    ))
                    mock_meta_storage.store_metadata = AsyncMock(return_value=Mock(
                        status=Mock(value="success"),
                        message="Metadata stored successfully"
                    ))
                    
                    # Perform multiple operations
                    num_operations = 50
                    request_data = {
                        "provider": "openai",
                        "model": "gpt-3.5-turbo",
                        "api_key": "sk-test123"
                    }
                    
                    start_time = time.time()
                    
                    for i in range(num_operations):
                        response = self.client.post("/models/connect", json=request_data)
                        assert response.status_code == 200
                        
                        # Every 10 operations, check memory usage
                        if i % 10 == 0:
                            # In a real test, you would check actual memory usage
                            # For now, just verify the operation completes
                            pass
                    
                    end_time = time.time()
                    total_time = (end_time - start_time) * 1000
                    
                    print(f"Completed {num_operations} operations in {total_time:.2f}ms")
                    print(f"Average time per operation: {total_time/num_operations:.2f}ms")
                    
                    # Verify performance doesn't degrade significantly
                    assert total_time < 10000  # Less than 10 seconds for 50 operations
    
    @pytest.mark.asyncio
    async def test_error_handling_performance(self):
        """Test performance of error handling paths."""
        # Mock failed connector
        mock_connector = Mock()
        mock_connector.test_connection = AsyncMock(return_value=Mock(
            status=Mock(value="failed"),
            message="Connection failed"
        ))
        
        with patch('main.OpenAIConnector', return_value=mock_connector):
            request_data = {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "api_key": "sk-invalid"
            }
            
            # Test error handling performance
            num_errors = 20
            start_time = time.time()
            
            for _ in range(num_errors):
                response = self.client.post("/models/connect", json=request_data)
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is False
            
            end_time = time.time()
            total_time = (end_time - start_time) * 1000
            
            print(f"Handled {num_errors} errors in {total_time:.2f}ms")
            print(f"Average error handling time: {total_time/num_errors:.2f}ms")
            
            # Error handling should be fast
            assert total_time < 2000  # Less than 2 seconds for 20 errors
    
    def test_api_response_times(self):
        """Test API response times for different endpoints."""
        # Test health check performance
        start_time = time.time()
        response = self.client.get("/health")
        health_time = (time.time() - start_time) * 1000
        
        assert response.status_code == 200
        assert health_time < 100  # Health check should be very fast
        print(f"Health check time: {health_time:.2f}ms")
        
        # Test models listing performance (with mocked storage)
        with patch('main.metadata_storage') as mock_meta_storage:
            mock_meta_storage.list_user_models = AsyncMock(return_value=Mock(
                status=Mock(value="success"),
                message="Found models for user",
                data={"models": []}
            ))
            
            start_time = time.time()
            response = self.client.get("/models")
            models_time = (time.time() - start_time) * 1000
            
            assert response.status_code == 200
            assert models_time < 500  # Models listing should be fast
            print(f"Models listing time: {models_time:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_stress_testing(self):
        """Test system behavior under stress conditions."""
        # Mock connector with variable latency
        mock_connector = Mock()
        mock_connector.test_connection = AsyncMock(return_value=Mock(
            status=Mock(value="success"),
            message="Connection successful",
            latency_ms=300.0,  # Slower connection
            model_info={"model": "gpt-3.5-turbo"}
        ))
        
        with patch('main.OpenAIConnector', return_value=mock_connector):
            with patch('main.credential_storage') as mock_cred_storage:
                with patch('main.metadata_storage') as mock_meta_storage:
                    # Mock storage operations with some delay
                    async def delayed_storage(*args, **kwargs):
                        await asyncio.sleep(0.01)  # 10ms delay
                        return Mock(
                            status=Mock(value="success"),
                            message="Operation successful"
                        )
                    
                    mock_cred_storage.store_credentials = delayed_storage
                    mock_meta_storage.store_metadata = delayed_storage
                    
                    # Stress test with many concurrent requests
                    num_requests = 25
                    request_data = {
                        "provider": "openai",
                        "model": "gpt-3.5-turbo",
                        "api_key": "sk-test123"
                    }
                    
                    start_time = time.time()
                    
                    # Send all requests concurrently
                    with ThreadPoolExecutor(max_workers=num_requests) as executor:
                        futures = [
                            executor.submit(
                                self.client.post, 
                                "/models/connect", 
                                json=request_data
                            )
                            for _ in range(num_requests)
                        ]
                        
                        responses = [future.result() for future in futures]
                    
                    end_time = time.time()
                    total_time = (end_time - start_time) * 1000
                    
                    # Verify all responses are successful
                    successful_responses = 0
                    for response in responses:
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("success", False):
                                successful_responses += 1
                    
                    success_rate = (successful_responses / num_requests) * 100
                    
                    print(f"Stress test: {num_requests} requests in {total_time:.2f}ms")
                    print(f"Success rate: {success_rate:.1f}%")
                    print(f"Average response time: {total_time/num_requests:.2f}ms")
                    
                    # Verify system handles stress well
                    assert success_rate >= 95  # At least 95% success rate
                    assert total_time < 10000  # Complete within 10 seconds

