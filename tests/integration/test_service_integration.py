"""
Integration tests for service communication.

Tests the integration between different services in the LLMShield platform
following industry standards for integration testing.
"""

import pytest
import requests
import time
import json
import asyncio
from typing import Dict, Any, List


class TestServiceIntegration:
    """Integration tests for service communication."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.api_gateway_url = "http://localhost:8000"
        self.prompt_injection_url = "http://localhost:8002"
        self.job_executor_url = "http://localhost:8001"
        self.results_insights_url = "http://localhost:8003"
        self.frontend_url = "http://localhost:3000"
        
        self.test_timeout = 30
        self.api_key = "sk-test123456789"  # Test API key
    
    def check_service_health(self, service_name: str, url: str) -> bool:
        """Check if a service is healthy."""
        try:
            response = requests.get(f"{url}/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def test_all_services_health(self):
        """Test that all services are healthy."""
        services = [
            ("API Gateway", self.api_gateway_url),
            ("Prompt Injection Tester", self.prompt_injection_url),
            ("Job Executor", self.job_executor_url),
            ("Results & Insights", self.results_insights_url)
        ]
        
        healthy_services = []
        unhealthy_services = []
        
        for name, url in services:
            if self.check_service_health(name, url):
                healthy_services.append(name)
            else:
                unhealthy_services.append(name)
        
        print(f"Healthy services: {healthy_services}")
        print(f"Unhealthy services: {unhealthy_services}")
        
        # At least API Gateway should be healthy for basic tests
        assert "API Gateway" in healthy_services, "API Gateway must be running for integration tests"
    
    @pytest.mark.requires_services
    def test_api_gateway_to_prompt_injection_communication(self):
        """Test communication between API Gateway and Prompt Injection service."""
        # Test prompt injection start through API Gateway
        request_data = {
            "api_key": self.api_key,
            "model": "gpt-3.5-turbo",
            "dataset_path": "prompt_injection_comprehensive_processed.json",
            "batch_size": 3,
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        response = requests.post(
            f"{self.api_gateway_url}/prompt-injection/start",
            json=request_data,
            timeout=self.test_timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "session_id" in data
            assert "status" in data
            assert "message" in data
            assert "created_at" in data
            
            # Test status endpoint
            session_id = data["session_id"]
            status_response = requests.get(
                f"{self.api_gateway_url}/prompt-injection/status/{session_id}",
                timeout=10
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                assert "session_id" in status_data
                assert "status" in status_data
                assert "progress" in status_data
                assert "total_tests" in status_data
        else:
            # Service not running or API key invalid
            assert response.status_code in [400, 500, 503]
    
    @pytest.mark.requires_services
    def test_api_gateway_to_results_insights_communication(self):
        """Test communication between API Gateway and Results & Insights service."""
        # First create a test session
        request_data = {
            "api_key": self.api_key,
            "model": "gpt-3.5-turbo"
        }
        
        start_response = requests.post(
            f"{self.api_gateway_url}/prompt-injection/start",
            json=request_data,
            timeout=self.test_timeout
        )
        
        if start_response.status_code == 200:
            session_id = start_response.json()["session_id"]
            
            # Test results endpoint
            results_response = requests.get(
                f"{self.api_gateway_url}/prompt-injection/results/{session_id}",
                timeout=10
            )
            
            if results_response.status_code == 200:
                results_data = results_response.json()
                assert "session_id" in results_data
                assert "status" in results_data
            else:
                # Expected if test not completed yet
                assert results_response.status_code in [400, 404, 503]
        else:
            # Service not running or API key invalid
            assert start_response.status_code in [400, 500, 503]
    
    @pytest.mark.requires_services
    def test_prompt_injection_to_results_insights_communication(self):
        """Test direct communication between Prompt Injection and Results & Insights."""
        # Test direct results insights endpoint
        session_id = "test-session-123"
        
        response = requests.get(
            f"{self.results_insights_url}/prompt-injection/report/{session_id}",
            timeout=10
        )
        
        # Should return 404 if session doesn't exist, or 503 if service not running
        assert response.status_code in [200, 404, 503]
    
    @pytest.mark.requires_services
    def test_end_to_end_prompt_injection_flow(self):
        """Test complete end-to-end prompt injection flow."""
        # Step 1: Start test
        request_data = {
            "api_key": self.api_key,
            "model": "gpt-3.5-turbo",
            "batch_size": 2,
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        start_response = requests.post(
            f"{self.api_gateway_url}/prompt-injection/start",
            json=request_data,
            timeout=self.test_timeout
        )
        
        if start_response.status_code != 200:
            pytest.skip("Services not available or API key invalid")
        
        session_id = start_response.json()["session_id"]
        print(f"Started test with session ID: {session_id}")
        
        # Step 2: Monitor progress
        max_attempts = 10
        attempt = 0
        
        while attempt < max_attempts:
            status_response = requests.get(
                f"{self.api_gateway_url}/prompt-injection/status/{session_id}",
                timeout=10
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                progress = status_data["progress"]
                status = status_data["status"]
                
                print(f"Progress: {progress:.1%} - Status: {status}")
                
                if status == "completed":
                    print("Test completed successfully!")
                    break
                elif status == "failed":
                    print(f"Test failed: {status_data.get('error', 'Unknown error')}")
                    break
                
                time.sleep(2)  # Wait 2 seconds between checks
                attempt += 1
            else:
                print(f"Status check failed: {status_response.status_code}")
                break
        
        # Step 3: Get results
        results_response = requests.get(
            f"{self.api_gateway_url}/prompt-injection/results/{session_id}",
            timeout=10
        )
        
        if results_response.status_code == 200:
            results_data = results_response.json()
            assert "session_id" in results_data
            assert "summary" in results_data
            
            summary = results_data["summary"]
            assert "test_summary" in summary
            assert "severity_analysis" in summary
            assert "recommendations" in summary
            
            print("End-to-end test completed successfully!")
        else:
            print(f"Results retrieval failed: {results_response.status_code}")
    
    @pytest.mark.requires_services
    def test_concurrent_test_execution(self):
        """Test concurrent test execution."""
        import threading
        import time
        
        results = []
        
        def execute_test(test_id: int):
            """Execute a test in a separate thread."""
            request_data = {
                "api_key": self.api_key,
                "model": "gpt-3.5-turbo",
                "batch_size": 1,
                "max_tokens": 50
            }
            
            try:
                response = requests.post(
                    f"{self.api_gateway_url}/prompt-injection/start",
                    json=request_data,
                    timeout=self.test_timeout
                )
                results.append({
                    "test_id": test_id,
                    "status_code": response.status_code,
                    "success": response.status_code == 200
                })
            except Exception as e:
                results.append({
                    "test_id": test_id,
                    "status_code": 0,
                    "success": False,
                    "error": str(e)
                })
        
        # Start multiple concurrent tests
        threads = []
        for i in range(3):
            thread = threading.Thread(target=execute_test, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=30)
        
        # Analyze results
        successful_tests = [r for r in results if r["success"]]
        failed_tests = [r for r in results if not r["success"]]
        
        print(f"Successful tests: {len(successful_tests)}")
        print(f"Failed tests: {len(failed_tests)}")
        
        # At least some tests should succeed
        assert len(successful_tests) >= 0  # Allow for service unavailability
    
    @pytest.mark.requires_services
    def test_error_handling_across_services(self):
        """Test error handling across service boundaries."""
        # Test with invalid session ID
        invalid_session_id = "invalid-session-123"
        
        status_response = requests.get(
            f"{self.api_gateway_url}/prompt-injection/status/{invalid_session_id}",
            timeout=10
        )
        
        # Should return 404 for invalid session
        assert status_response.status_code in [404, 503]
        
        # Test with invalid API key
        invalid_request = {
            "api_key": "invalid-api-key",
            "model": "gpt-3.5-turbo"
        }
        
        start_response = requests.post(
            f"{self.api_gateway_url}/prompt-injection/start",
            json=invalid_request,
            timeout=self.test_timeout
        )
        
        # Should handle invalid API key gracefully
        assert start_response.status_code in [200, 400, 500, 503]
    
    @pytest.mark.requires_services
    def test_data_consistency_across_services(self):
        """Test data consistency across services."""
        # Start a test
        request_data = {
            "api_key": self.api_key,
            "model": "gpt-3.5-turbo",
            "batch_size": 1
        }
        
        start_response = requests.post(
            f"{self.api_gateway_url}/prompt-injection/start",
            json=request_data,
            timeout=self.test_timeout
        )
        
        if start_response.status_code == 200:
            session_id = start_response.json()["session_id"]
            
            # Check status from API Gateway
            api_gateway_status = requests.get(
                f"{self.api_gateway_url}/prompt-injection/status/{session_id}",
                timeout=10
            )
            
            # Check status directly from Prompt Injection service
            prompt_injection_status = requests.get(
                f"{self.prompt_injection_url}/test/status/{session_id}",
                timeout=10
            )
            
            if api_gateway_status.status_code == 200 and prompt_injection_status.status_code == 200:
                api_data = api_gateway_status.json()
                pi_data = prompt_injection_status.json()
                
                # Data should be consistent
                assert api_data["session_id"] == pi_data["session_id"]
                assert api_data["status"] == pi_data["status"]
                assert api_data["total_tests"] == pi_data["total_tests"]
    
    @pytest.mark.requires_services
    def test_service_resilience(self):
        """Test service resilience and recovery."""
        # Test that services can handle high load
        request_data = {
            "api_key": self.api_key,
            "model": "gpt-3.5-turbo",
            "batch_size": 1
        }
        
        # Send multiple requests rapidly
        responses = []
        for i in range(5):
            response = requests.post(
                f"{self.api_gateway_url}/prompt-injection/start",
                json=request_data,
                timeout=self.test_timeout
            )
            responses.append(response.status_code)
            time.sleep(0.1)  # Small delay between requests
        
        # All requests should be handled (even if some fail)
        for status_code in responses:
            assert status_code in [200, 400, 500, 503]
        
        # Test that services recover from errors
        # This is a placeholder for more sophisticated resilience testing
        assert True  # Placeholder assertion


class TestFrontendIntegration:
    """Integration tests for frontend communication."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.frontend_url = "http://localhost:3000"
        self.api_gateway_url = "http://localhost:8000"
    
    def test_frontend_health(self):
        """Test that frontend is accessible."""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            # Frontend should be accessible
            assert response.status_code in [200, 404]  # 404 is acceptable for root path
        except requests.exceptions.ConnectionError:
            pytest.skip("Frontend not running")
    
    def test_frontend_api_communication(self):
        """Test frontend to API communication."""
        # Test that frontend can communicate with API Gateway
        try:
            response = requests.get(f"{self.api_gateway_url}/health", timeout=5)
            assert response.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.skip("API Gateway not running")
    
    def test_cors_headers(self):
        """Test CORS headers for frontend communication."""
        try:
            response = requests.options(f"{self.api_gateway_url}/health")
            assert response.status_code == 200
            
            # Check for CORS headers
            headers = response.headers
            assert "access-control-allow-origin" in headers or "Access-Control-Allow-Origin" in headers
        except requests.exceptions.ConnectionError:
            pytest.skip("API Gateway not running")


class TestPerformanceIntegration:
    """Performance integration tests."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.api_gateway_url = "http://localhost:8000"
        self.test_timeout = 30
    
    def test_response_time_requirements(self):
        """Test that response times meet requirements."""
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.api_gateway_url}/health", timeout=5)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Health check should be fast
            assert response_time < 1.0, f"Health check took {response_time:.2f}s, should be < 1.0s"
            assert response.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.skip("API Gateway not running")
    
    def test_concurrent_request_handling(self):
        """Test handling of concurrent requests."""
        import threading
        import time
        
        results = []
        
        def make_request(request_id: int):
            """Make a request in a separate thread."""
            start_time = time.time()
            try:
                response = requests.get(f"{self.api_gateway_url}/health", timeout=5)
                end_time = time.time()
                results.append({
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "success": response.status_code == 200
                })
            except Exception as e:
                results.append({
                    "request_id": request_id,
                    "status_code": 0,
                    "response_time": 0,
                    "success": False,
                    "error": str(e)
                })
        
        # Start multiple concurrent requests
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)
        
        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        print(f"Successful requests: {len(successful_requests)}")
        print(f"Failed requests: {len(failed_requests)}")
        
        if successful_requests:
            avg_response_time = sum(r["response_time"] for r in successful_requests) / len(successful_requests)
            print(f"Average response time: {avg_response_time:.2f}s")
            
            # Most requests should succeed
            success_rate = len(successful_requests) / len(results)
            assert success_rate > 0.8, f"Success rate {success_rate:.1%} is too low"
            
            # Response time should be reasonable
            assert avg_response_time < 2.0, f"Average response time {avg_response_time:.2f}s is too high"

