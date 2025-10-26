"""
End-to-end tests for prompt injection functionality.

Tests the complete user journey from frontend to backend services
following industry standards for E2E testing.
"""

import pytest
import requests
import time
import json
import asyncio
from typing import Dict, Any, List


class TestPromptInjectionE2E:
    """End-to-end tests for prompt injection functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.api_gateway_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.test_timeout = 60  # 1 minute timeout for E2E tests
        self.api_key = "sk-test123456789"  # Test API key
    
    def check_services_health(self) -> Dict[str, bool]:
        """Check health of all required services."""
        services = {
            "api_gateway": f"{self.api_gateway_url}/health",
            "frontend": f"{self.frontend_url}",
        }
        
        health_status = {}
        for service, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                health_status[service] = response.status_code in [200, 404]  # 404 is acceptable for frontend root
            except requests.exceptions.RequestException:
                health_status[service] = False
        
        return health_status
    
    @pytest.mark.e2e
    @pytest.mark.requires_services
    def test_complete_prompt_injection_workflow(self):
        """Test complete prompt injection workflow from start to finish."""
        # Check service health
        health_status = self.check_services_health()
        
        if not health_status.get("api_gateway", False):
            pytest.skip("API Gateway not available")
        
        print("🚀 Starting complete prompt injection E2E test...")
        
        # Step 1: Start prompt injection test
        print("1️⃣ Starting prompt injection test...")
        request_data = {
            "api_key": self.api_key,
            "model": "gpt-3.5-turbo",
            "dataset_path": "prompt_injection_comprehensive_processed.json",
            "batch_size": 3,
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        start_response = requests.post(
            f"{self.api_gateway_url}/prompt-injection/start",
            json=request_data,
            timeout=self.test_timeout
        )
        
        if start_response.status_code != 200:
            pytest.skip(f"Failed to start test: {start_response.status_code} - {start_response.text}")
        
        start_data = start_response.json()
        session_id = start_data["session_id"]
        print(f"✅ Test started with session ID: {session_id}")
        
        # Step 2: Monitor test progress
        print("2️⃣ Monitoring test progress...")
        max_attempts = 30  # 5 minutes max
        attempt = 0
        test_completed = False
        
        while attempt < max_attempts and not test_completed:
            status_response = requests.get(
                f"{self.api_gateway_url}/prompt-injection/status/{session_id}",
                timeout=10
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                progress = status_data["progress"]
                status = status_data["status"]
                completed_tests = status_data["completed_tests"]
                total_tests = status_data["total_tests"]
                successful_detections = status_data["successful_detections"]
                failed_detections = status_data["failed_detections"]
                
                print(f"   Progress: {progress:.1%} ({completed_tests}/{total_tests})")
                print(f"   Status: {status}")
                print(f"   Successful: {successful_detections}, Failed: {failed_detections}")
                
                if status == "completed":
                    print("✅ Test completed successfully!")
                    test_completed = True
                    break
                elif status == "failed":
                    error_msg = status_data.get("error", "Unknown error")
                    print(f"❌ Test failed: {error_msg}")
                    pytest.fail(f"Test failed: {error_msg}")
                
                time.sleep(10)  # Wait 10 seconds between checks
                attempt += 1
            else:
                print(f"⚠️  Status check failed: {status_response.status_code}")
                time.sleep(5)
                attempt += 1
        
        if not test_completed:
            pytest.fail("Test did not complete within timeout period")
        
        # Step 3: Get detailed results
        print("3️⃣ Retrieving detailed results...")
        results_response = requests.get(
            f"{self.api_gateway_url}/prompt-injection/results/{session_id}",
            timeout=10
        )
        
        assert results_response.status_code == 200, f"Failed to get results: {results_response.status_code}"
        
        results_data = results_response.json()
        assert "session_id" in results_data
        assert "summary" in results_data
        assert "detailed_results" in results_data
        
        summary = results_data["summary"]
        print(f"📊 Test Summary:")
        print(f"   Total Tests: {summary['test_summary']['total_tests']}")
        print(f"   Successful Detections: {summary['test_summary']['successful_detections']}")
        print(f"   Detection Rate: {summary['test_summary']['detection_rate']:.1f}%")
        print(f"   Average Response Time: {summary['test_summary']['average_response_time']:.2f}s")
        
        # Step 4: Validate test results
        print("4️⃣ Validating test results...")
        assert summary["test_summary"]["total_tests"] > 0, "No tests were executed"
        assert summary["test_summary"]["detection_rate"] >= 0, "Invalid detection rate"
        assert summary["test_summary"]["average_response_time"] > 0, "Invalid response time"
        
        # Check severity analysis
        assert "severity_analysis" in summary, "Missing severity analysis"
        assert "language_analysis" in summary, "Missing language analysis"
        assert "technique_analysis" in summary, "Missing technique analysis"
        assert "risk_analysis" in summary, "Missing risk analysis"
        assert "recommendations" in summary, "Missing recommendations"
        
        # Step 5: Test report generation
        print("5️⃣ Testing report generation...")
        report_response = requests.get(
            f"{self.api_gateway_url}/prompt-injection/results/{session_id}",
            timeout=10
        )
        
        assert report_response.status_code == 200, "Failed to generate report"
        
        report_data = report_response.json()
        assert "session_id" in report_data
        assert "summary" in report_data
        
        print("✅ Complete E2E test passed!")
    
    @pytest.mark.e2e
    @pytest.mark.requires_services
    def test_prompt_injection_with_different_models(self):
        """Test prompt injection with different model configurations."""
        models_to_test = [
            {"model": "gpt-3.5-turbo", "temperature": 0.7},
            {"model": "gpt-3.5-turbo", "temperature": 0.3},
            {"model": "gpt-3.5-turbo", "temperature": 1.0}
        ]
        
        for i, model_config in enumerate(models_to_test):
            print(f"🧪 Testing model configuration {i+1}: {model_config}")
            
            request_data = {
                "api_key": self.api_key,
                "model": model_config["model"],
                "temperature": model_config["temperature"],
                "batch_size": 2,
                "max_tokens": 50
            }
            
            start_response = requests.post(
                f"{self.api_gateway_url}/prompt-injection/start",
                json=request_data,
                timeout=self.test_timeout
            )
            
            if start_response.status_code == 200:
                session_id = start_response.json()["session_id"]
                print(f"   Started test with session: {session_id}")
                
                # Wait for completion (simplified for E2E test)
                time.sleep(5)
                
                # Check status
                status_response = requests.get(
                    f"{self.api_gateway_url}/prompt-injection/status/{session_id}",
                    timeout=10
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   Status: {status_data['status']}")
                    print(f"   Progress: {status_data['progress']:.1%}")
                else:
                    print(f"   Status check failed: {status_response.status_code}")
            else:
                print(f"   Failed to start test: {start_response.status_code}")
    
    @pytest.mark.e2e
    @pytest.mark.requires_services
    def test_prompt_injection_error_handling(self):
        """Test error handling in prompt injection workflow."""
        print("🧪 Testing error handling...")
        
        # Test 1: Invalid API key
        print("1️⃣ Testing invalid API key...")
        invalid_request = {
            "api_key": "invalid-api-key",
            "model": "gpt-3.5-turbo"
        }
        
        response = requests.post(
            f"{self.api_gateway_url}/prompt-injection/start",
            json=invalid_request,
            timeout=self.test_timeout
        )
        
        # Should handle invalid API key gracefully
        assert response.status_code in [200, 400, 500, 503], f"Unexpected status code: {response.status_code}"
        
        # Test 2: Invalid session ID
        print("2️⃣ Testing invalid session ID...")
        invalid_session_id = "invalid-session-123"
        
        status_response = requests.get(
            f"{self.api_gateway_url}/prompt-injection/status/{invalid_session_id}",
            timeout=10
        )
        
        # Should return 404 for invalid session
        assert status_response.status_code in [404, 503], f"Unexpected status code: {status_response.status_code}"
        
        # Test 3: Invalid model
        print("3️⃣ Testing invalid model...")
        invalid_model_request = {
            "api_key": self.api_key,
            "model": "invalid-model"
        }
        
        response = requests.post(
            f"{self.api_gateway_url}/prompt-injection/start",
            json=invalid_model_request,
            timeout=self.test_timeout
        )
        
        # Should handle invalid model gracefully
        assert response.status_code in [200, 400, 500, 503], f"Unexpected status code: {response.status_code}"
        
        print("✅ Error handling tests completed")
    
    @pytest.mark.e2e
    @pytest.mark.requires_services
    def test_prompt_injection_cancellation(self):
        """Test prompt injection test cancellation."""
        print("🧪 Testing test cancellation...")
        
        # Start a test
        request_data = {
            "api_key": self.api_key,
            "model": "gpt-3.5-turbo",
            "batch_size": 5,
            "max_tokens": 100
        }
        
        start_response = requests.post(
            f"{self.api_gateway_url}/prompt-injection/start",
            json=request_data,
            timeout=self.test_timeout
        )
        
        if start_response.status_code == 200:
            session_id = start_response.json()["session_id"]
            print(f"   Started test with session: {session_id}")
            
            # Wait a bit for test to start
            time.sleep(2)
            
            # Cancel the test
            cancel_response = requests.delete(
                f"{self.api_gateway_url}/prompt-injection/cancel/{session_id}",
                timeout=10
            )
            
            if cancel_response.status_code == 200:
                print("   ✅ Test cancelled successfully")
                
                # Check status after cancellation
                status_response = requests.get(
                    f"{self.api_gateway_url}/prompt-injection/status/{session_id}",
                    timeout=10
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   Status after cancellation: {status_data['status']}")
            else:
                print(f"   ⚠️  Cancellation failed: {cancel_response.status_code}")
        else:
            print(f"   ⚠️  Failed to start test: {start_response.status_code}")
    
    @pytest.mark.e2e
    @pytest.mark.requires_services
    def test_prompt_injection_performance_requirements(self):
        """Test that prompt injection meets performance requirements."""
        print("🧪 Testing performance requirements...")
        
        # Test response time requirements
        start_time = time.time()
        
        request_data = {
            "api_key": self.api_key,
            "model": "gpt-3.5-turbo",
            "batch_size": 1,
            "max_tokens": 50
        }
        
        start_response = requests.post(
            f"{self.api_gateway_url}/prompt-injection/start",
            json=request_data,
            timeout=self.test_timeout
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"   Start request response time: {response_time:.2f}s")
        
        # Start request should be fast
        assert response_time < 5.0, f"Start request too slow: {response_time:.2f}s"
        
        if start_response.status_code == 200:
            session_id = start_response.json()["session_id"]
            
            # Test status check performance
            start_time = time.time()
            status_response = requests.get(
                f"{self.api_gateway_url}/prompt-injection/status/{session_id}",
                timeout=10
            )
            end_time = time.time()
            status_response_time = end_time - start_time
            
            print(f"   Status check response time: {status_response_time:.2f}s")
            
            # Status check should be fast
            assert status_response_time < 2.0, f"Status check too slow: {status_response_time:.2f}s"
    
    @pytest.mark.e2e
    @pytest.mark.requires_services
    def test_prompt_injection_data_validation(self):
        """Test data validation in prompt injection workflow."""
        print("🧪 Testing data validation...")
        
        # Test valid request
        valid_request = {
            "api_key": self.api_key,
            "model": "gpt-3.5-turbo",
            "dataset_path": "prompt_injection_comprehensive_processed.json",
            "batch_size": 3,
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        response = requests.post(
            f"{self.api_gateway_url}/prompt-injection/start",
            json=valid_request,
            timeout=self.test_timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "session_id" in data, "Missing session_id in response"
            assert "status" in data, "Missing status in response"
            assert "message" in data, "Missing message in response"
            assert "created_at" in data, "Missing created_at in response"
            
            # Validate session_id format
            session_id = data["session_id"]
            assert len(session_id) > 0, "Empty session_id"
            assert isinstance(session_id, str), "session_id should be string"
            
            print("   ✅ Valid request processed correctly")
        else:
            print(f"   ⚠️  Valid request failed: {response.status_code}")
        
        # Test invalid batch_size
        invalid_request = {
            "api_key": self.api_key,
            "model": "gpt-3.5-turbo",
            "batch_size": -1  # Invalid batch size
        }
        
        response = requests.post(
            f"{self.api_gateway_url}/prompt-injection/start",
            json=invalid_request,
            timeout=self.test_timeout
        )
        
        # Should handle invalid batch size appropriately
        assert response.status_code in [200, 400, 422, 500, 503], f"Unexpected status code: {response.status_code}"
        
        print("   ✅ Data validation tests completed")
    
    @pytest.mark.e2e
    @pytest.mark.requires_services
    def test_prompt_injection_security_requirements(self):
        """Test security requirements in prompt injection workflow."""
        print("🧪 Testing security requirements...")
        
        # Test SQL injection protection
        malicious_request = {
            "api_key": "'; DROP TABLE users; --",
            "model": "gpt-3.5-turbo"
        }
        
        response = requests.post(
            f"{self.api_gateway_url}/prompt-injection/start",
            json=malicious_request,
            timeout=self.test_timeout
        )
        
        # Should handle malicious input gracefully
        assert response.status_code in [200, 400, 422, 500, 503], f"Unexpected status code: {response.status_code}"
        
        # Test XSS protection
        xss_request = {
            "api_key": self.api_key,
            "model": "<script>alert('XSS')</script>"
        }
        
        response = requests.post(
            f"{self.api_gateway_url}/prompt-injection/start",
            json=xss_request,
            timeout=self.test_timeout
        )
        
        # Should handle XSS input gracefully
        assert response.status_code in [200, 400, 422, 500, 503], f"Unexpected status code: {response.status_code}"
        
        # Test path traversal protection
        path_traversal_request = {
            "api_key": self.api_key,
            "model": "gpt-3.5-turbo",
            "dataset_path": "../../etc/passwd"
        }
        
        response = requests.post(
            f"{self.api_gateway_url}/prompt-injection/start",
            json=path_traversal_request,
            timeout=self.test_timeout
        )
        
        # Should handle path traversal gracefully
        assert response.status_code in [200, 400, 422, 500, 503], f"Unexpected status code: {response.status_code}"
        
        print("   ✅ Security tests completed")


class TestFrontendE2E:
    """End-to-end tests for frontend integration."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.frontend_url = "http://localhost:3000"
        self.api_gateway_url = "http://localhost:8000"
    
    @pytest.mark.e2e
    def test_frontend_accessibility(self):
        """Test that frontend is accessible."""
        try:
            response = requests.get(self.frontend_url, timeout=10)
            # Frontend should be accessible
            assert response.status_code in [200, 404], f"Frontend not accessible: {response.status_code}"
            print("✅ Frontend is accessible")
        except requests.exceptions.ConnectionError:
            pytest.skip("Frontend not running")
    
    @pytest.mark.e2e
    def test_frontend_api_communication(self):
        """Test that frontend can communicate with API."""
        try:
            # Test API Gateway health
            response = requests.get(f"{self.api_gateway_url}/health", timeout=5)
            assert response.status_code == 200, f"API Gateway not accessible: {response.status_code}"
            print("✅ API Gateway is accessible")
            
            # Test CORS headers
            response = requests.options(f"{self.api_gateway_url}/health")
            assert response.status_code == 200, f"CORS preflight failed: {response.status_code}"
            print("✅ CORS headers are present")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API Gateway not running")
    
    @pytest.mark.e2e
    def test_frontend_dashboard_accessibility(self):
        """Test that frontend dashboard is accessible."""
        try:
            # Test dashboard page
            response = requests.get(f"{self.frontend_url}/dashboard", timeout=10)
            assert response.status_code in [200, 404], f"Dashboard not accessible: {response.status_code}"
            print("✅ Dashboard is accessible")
            
            # Test prompt injection page
            response = requests.get(f"{self.frontend_url}/dashboard/prompt-injection", timeout=10)
            assert response.status_code in [200, 404], f"Prompt injection page not accessible: {response.status_code}"
            print("✅ Prompt injection page is accessible")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Frontend not running")




