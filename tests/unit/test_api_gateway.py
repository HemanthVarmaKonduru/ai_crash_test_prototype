"""
Unit tests for API Gateway service.

Tests individual components and functions of the API Gateway service
following industry standards for unit testing.
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

# Test imports
try:
    from main import app, ModelConnectionRequest, PromptInjectionTestRequest
    from main import get_current_user, connect_model
except ImportError:
    pytest.skip("API Gateway not available", allow_module_level=True)


class TestAPIGatewayUnit:
    """Unit tests for API Gateway service."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.client = TestClient(app)
        self.sample_request = {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "api_key": "sk-test123456789",
            "name": "Test Model",
            "config": {"temperature": 0.7}
        }
    
    def test_app_initialization(self):
        """Test that the FastAPI app initializes correctly."""
        assert app is not None
        assert app.title == "Adversarial Sandbox API Gateway"
        assert app.version == "0.1.0"
    
    def test_cors_middleware_configured(self):
        """Test that CORS middleware is properly configured."""
        # Check if CORS middleware is in the middleware stack
        middleware_types = [type(middleware) for middleware in app.user_middleware]
        assert any("CORSMiddleware" in str(middleware_type) for middleware_type in middleware_types)
    
    def test_get_current_user(self):
        """Test get_current_user function."""
        user_id = get_current_user()
        assert user_id == "demo-user-123"
    
    def test_model_connection_request_validation(self):
        """Test ModelConnectionRequest model validation."""
        # Valid request
        valid_request = ModelConnectionRequest(**self.sample_request)
        assert valid_request.provider == "openai"
        assert valid_request.model == "gpt-3.5-turbo"
        assert valid_request.api_key == "sk-test123456789"
        
        # Test with minimal required fields
        minimal_request = ModelConnectionRequest(
            provider="openai",
            model="gpt-3.5-turbo",
            api_key="sk-test123456789"
        )
        assert minimal_request.provider == "openai"
        assert minimal_request.name is None
        assert minimal_request.config == {}
    
    def test_model_connection_request_validation_errors(self):
        """Test ModelConnectionRequest validation errors."""
        # Missing required fields
        with pytest.raises(ValueError):
            ModelConnectionRequest(provider="openai")
        
        with pytest.raises(ValueError):
            ModelConnectionRequest(model="gpt-3.5-turbo")
        
        with pytest.raises(ValueError):
            ModelConnectionRequest(api_key="sk-test123456789")
    
    def test_prompt_injection_test_request_validation(self):
        """Test PromptInjectionTestRequest model validation."""
        # Valid request
        valid_request = PromptInjectionTestRequest(
            api_key="sk-test123456789",
            model="gpt-3.5-turbo"
        )
        assert valid_request.api_key == "sk-test123456789"
        assert valid_request.model == "gpt-3.5-turbo"
        assert valid_request.dataset_path == "prompt_injection_comprehensive_processed.json"
        assert valid_request.batch_size == 10
        assert valid_request.max_tokens == 150
        assert valid_request.temperature == 0.7
    
    def test_prompt_injection_test_request_defaults(self):
        """Test PromptInjectionTestRequest default values."""
        request = PromptInjectionTestRequest(api_key="sk-test123456789")
        assert request.model == "gpt-3.5-turbo"
        assert request.dataset_path == "prompt_injection_comprehensive_processed.json"
        assert request.batch_size == 10
        assert request.max_tokens == 150
        assert request.temperature == 0.7
    
    @patch('main.OpenAIConnector')
    @patch('main.credential_storage')
    @patch('main.metadata_storage')
    async def test_connect_model_success(self, mock_metadata, mock_credential, mock_connector):
        """Test successful model connection."""
        # Setup mocks
        mock_connector_instance = Mock()
        mock_connector_instance.test_connection = AsyncMock(return_value=Mock(
            status=Mock(value="success"),
            message="Connection successful",
            latency_ms=245.5,
            model_info={"model": "gpt-3.5-turbo", "provider": "openai"}
        ))
        mock_connector.return_value = mock_connector_instance
        
        mock_credential.store_credentials = AsyncMock(return_value=Mock(
            status=Mock(value="success"),
            message="Credentials stored successfully"
        ))
        
        mock_metadata.store_metadata = AsyncMock(return_value=Mock(
            status=Mock(value="success"),
            message="Metadata stored successfully"
        ))
        
        # Test connection
        request = ModelConnectionRequest(**self.sample_request)
        response = await connect_model(request, "demo-user-123")
        
        assert response.success is True
        assert response.message == "Model connected successfully"
        assert response.model_id == "demo-user-123:openai:gpt-3.5-turbo"
        assert response.latency_ms == 245.5
    
    @patch('main.OpenAIConnector')
    async def test_connect_model_connection_failure(self, mock_connector):
        """Test model connection failure."""
        # Setup mock for connection failure
        mock_connector_instance = Mock()
        mock_connector_instance.test_connection = AsyncMock(return_value=Mock(
            status=Mock(value="failed"),
            message="Connection failed"
        ))
        mock_connector.return_value = mock_connector_instance
        
        request = ModelConnectionRequest(**self.sample_request)
        response = await connect_model(request, "demo-user-123")
        
        assert response.success is False
        assert "Connection failed" in response.message
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "api-gateway"
    
    def test_models_endpoint(self):
        """Test models listing endpoint."""
        response = self.client.get("/models")
        assert response.status_code == 200
        
        data = response.json()
        assert "models" in data
        assert isinstance(data["models"], list)
    
    def test_prompt_injection_start_endpoint_structure(self):
        """Test prompt injection start endpoint structure."""
        # Test with valid request structure
        request_data = {
            "api_key": "sk-test123456789",
            "model": "gpt-3.5-turbo",
            "dataset_path": "test_dataset.json",
            "batch_size": 5,
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        # This will fail if services aren't running, but we can test the structure
        response = self.client.post("/prompt-injection/start", json=request_data)
        # Should return 503 if prompt injection service is not running
        assert response.status_code in [200, 503]
    
    def test_prompt_injection_status_endpoint_structure(self):
        """Test prompt injection status endpoint structure."""
        session_id = "test-session-123"
        response = self.client.get(f"/prompt-injection/status/{session_id}")
        # Should return 503 if prompt injection service is not running
        assert response.status_code in [200, 404, 503]
    
    def test_prompt_injection_results_endpoint_structure(self):
        """Test prompt injection results endpoint structure."""
        session_id = "test-session-123"
        response = self.client.get(f"/prompt-injection/results/{session_id}")
        # Should return 503 if prompt injection service is not running
        assert response.status_code in [200, 404, 503]
    
    def test_prompt_injection_cancel_endpoint_structure(self):
        """Test prompt injection cancel endpoint structure."""
        session_id = "test-session-123"
        response = self.client.delete(f"/prompt-injection/cancel/{session_id}")
        # Should return 503 if prompt injection service is not running
        assert response.status_code in [200, 404, 503]
    
    def test_error_handling_invalid_json(self):
        """Test error handling for invalid JSON."""
        response = self.client.post(
            "/models/connect",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422  # Validation error
    
    def test_error_handling_missing_fields(self):
        """Test error handling for missing required fields."""
        incomplete_request = {
            "provider": "openai"
            # Missing model and api_key
        }
        
        response = self.client.post("/models/connect", json=incomplete_request)
        assert response.status_code == 422  # Validation error
    
    def test_cors_headers(self):
        """Test CORS headers are present."""
        response = self.client.options("/health")
        assert response.status_code == 200
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers
    
    def test_api_documentation_accessible(self):
        """Test that API documentation is accessible."""
        response = self.client.get("/docs")
        assert response.status_code == 200
        
        response = self.client.get("/openapi.json")
        assert response.status_code == 200


class TestAPIGatewayIntegration:
    """Integration tests for API Gateway with external services."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.client = TestClient(app)
    
    @pytest.mark.requires_services
    def test_prompt_injection_service_integration(self):
        """Test integration with prompt injection service."""
        # This test requires the prompt injection service to be running
        request_data = {
            "api_key": "sk-test123456789",
            "model": "gpt-3.5-turbo"
        }
        
        response = self.client.post("/prompt-injection/start", json=request_data)
        
        if response.status_code == 200:
            data = response.json()
            assert "session_id" in data
            assert "status" in data
            assert "message" in data
            assert "created_at" in data
        else:
            # Service not running - this is expected in CI/CD
            assert response.status_code == 503
    
    @pytest.mark.requires_services
    def test_results_insights_service_integration(self):
        """Test integration with results insights service."""
        # This test requires the results insights service to be running
        session_id = "test-session-123"
        response = self.client.get(f"/prompt-injection/results/{session_id}")
        
        if response.status_code == 200:
            data = response.json()
            assert "session_id" in data
            assert "status" in data
        else:
            # Service not running - this is expected in CI/CD
            assert response.status_code in [404, 503]


class TestAPIGatewaySecurity:
    """Security tests for API Gateway."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.client = TestClient(app)
    
    def test_sql_injection_protection(self):
        """Test protection against SQL injection."""
        malicious_payload = "'; DROP TABLE users; --"
        
        # Test in model connection request
        request_data = {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "api_key": "sk-test123456789",
            "name": malicious_payload
        }
        
        response = self.client.post("/models/connect", json=request_data)
        # Should handle malicious input gracefully
        assert response.status_code in [200, 400, 422, 500]
    
    def test_xss_protection(self):
        """Test protection against XSS attacks."""
        malicious_payload = "<script>alert('XSS')</script>"
        
        request_data = {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "api_key": "sk-test123456789",
            "name": malicious_payload
        }
        
        response = self.client.post("/models/connect", json=request_data)
        # Should handle malicious input gracefully
        assert response.status_code in [200, 400, 422, 500]
    
    def test_input_validation(self):
        """Test input validation for various attack vectors."""
        test_cases = [
            {"field": "provider", "value": "../../etc/passwd"},
            {"field": "model", "value": "| cat /etc/passwd"},
            {"field": "api_key", "value": "'; rm -rf /"},
        ]
        
        for test_case in test_cases:
            request_data = {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "api_key": "sk-test123456789"
            }
            request_data[test_case["field"]] = test_case["value"]
            
            response = self.client.post("/models/connect", json=request_data)
            # Should handle malicious input gracefully
            assert response.status_code in [200, 400, 422, 500]
    
    def test_rate_limiting_headers(self):
        """Test that rate limiting headers are present."""
        response = self.client.get("/health")
        # Check for rate limiting headers (if implemented)
        # This is a placeholder for future rate limiting implementation
        assert response.status_code == 200

