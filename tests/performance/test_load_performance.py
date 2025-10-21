"""
Performance and load tests for LLMShield platform.

Tests system performance under various load conditions
following industry standards for performance testing.
"""

import pytest
import requests
import time
import threading
import statistics
import psutil
import os
from typing import Dict, Any, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import json


class TestLoadPerformance:
    """Load testing for the LLMShield platform."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.api_gateway_url = "http://localhost:8000"
        self.prompt_injection_url = "http://localhost:8002"
        self.results_insights_url = "http://localhost:8003"
        self.api_key = "sk-test123456789"
        self.test_timeout = 30
    
    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system metrics."""
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_available": psutil.virtual_memory().available / (1024 * 1024 * 1024),  # GB
            "disk_usage": psutil.disk_usage('/').percent
        }
    
    def make_request(self, url: str, method: str = "GET", data: Dict = None, timeout: int = 10) -> Tuple[bool, float, int]:
        """Make a request and return success, response_time, status_code."""
        start_time = time.time()
        try:
            if method == "GET":
                response = requests.get(url, timeout=timeout)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=timeout)
            elif method == "DELETE":
                response = requests.delete(url, timeout=timeout)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return True, response_time, response.status_code
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            return False, response_time, 0
    
    @pytest.mark.performance
    def test_health_check_performance(self):
        """Test health check endpoint performance."""
        print("🧪 Testing health check performance...")
        
        # Test single request
        success, response_time, status_code = self.make_request(f"{self.api_gateway_url}/health")
        
        if success:
            assert status_code == 200, f"Health check failed: {status_code}"
            assert response_time < 1.0, f"Health check too slow: {response_time:.2f}s"
            print(f"   ✅ Single health check: {response_time:.3f}s")
        else:
            pytest.skip("API Gateway not available")
        
        # Test multiple concurrent requests
        num_requests = 10
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [
                executor.submit(self.make_request, f"{self.api_gateway_url}/health")
                for _ in range(num_requests)
            ]
            
            results = []
            for future in as_completed(futures):
                success, response_time, status_code = future.result()
                results.append((success, response_time, status_code))
        
        end_time = time.time()
        total_time = end_time - start_time
        
        successful_requests = [r for r in results if r[0]]
        response_times = [r[1] for r in successful_requests]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            print(f"   📊 Concurrent health checks ({num_requests} requests):")
            print(f"      Total time: {total_time:.2f}s")
            print(f"      Successful: {len(successful_requests)}/{num_requests}")
            print(f"      Avg response time: {avg_response_time:.3f}s")
            print(f"      Max response time: {max_response_time:.3f}s")
            print(f"      Min response time: {min_response_time:.3f}s")
            
            # Performance assertions
            assert len(successful_requests) >= num_requests * 0.9, f"Too many failed requests: {len(successful_requests)}/{num_requests}"
            assert avg_response_time < 2.0, f"Average response time too high: {avg_response_time:.3f}s"
            assert max_response_time < 5.0, f"Max response time too high: {max_response_time:.3f}s"
    
    @pytest.mark.performance
    def test_prompt_injection_start_performance(self):
        """Test prompt injection start endpoint performance."""
        print("🧪 Testing prompt injection start performance...")
        
        request_data = {
            "api_key": self.api_key,
            "model": "gpt-3.5-turbo",
            "batch_size": 1,
            "max_tokens": 50
        }
        
        # Test single request
        success, response_time, status_code = self.make_request(
            f"{self.api_gateway_url}/prompt-injection/start",
            method="POST",
            data=request_data,
            timeout=self.test_timeout
        )
        
        if success and status_code == 200:
            print(f"   ✅ Single start request: {response_time:.3f}s")
            
            # Performance requirements
            assert response_time < 10.0, f"Start request too slow: {response_time:.2f}s"
        else:
            print(f"   ⚠️  Start request failed: {status_code}")
            # Don't fail the test if service is not available
    
    @pytest.mark.performance
    def test_concurrent_prompt_injection_requests(self):
        """Test concurrent prompt injection requests."""
        print("🧪 Testing concurrent prompt injection requests...")
        
        request_data = {
            "api_key": self.api_key,
            "model": "gpt-3.5-turbo",
            "batch_size": 1,
            "max_tokens": 50
        }
        
        num_requests = 5  # Reduced for performance testing
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [
                executor.submit(
                    self.make_request,
                    f"{self.api_gateway_url}/prompt-injection/start",
                    "POST",
                    request_data,
                    self.test_timeout
                )
                for _ in range(num_requests)
            ]
            
            results = []
            for future in as_completed(futures):
                success, response_time, status_code = future.result()
                results.append((success, response_time, status_code))
        
        end_time = time.time()
        total_time = end_time - start_time
        
        successful_requests = [r for r in results if r[0] and r[2] in [200, 400, 500, 503]]
        response_times = [r[1] for r in successful_requests]
        
        print(f"   📊 Concurrent start requests ({num_requests} requests):")
        print(f"      Total time: {total_time:.2f}s")
        print(f"      Successful: {len(successful_requests)}/{num_requests}")
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            
            print(f"      Avg response time: {avg_response_time:.3f}s")
            print(f"      Max response time: {max_response_time:.3f}s")
            
            # Performance assertions
            assert len(successful_requests) >= num_requests * 0.8, f"Too many failed requests: {len(successful_requests)}/{num_requests}"
            assert avg_response_time < 15.0, f"Average response time too high: {avg_response_time:.3f}s"
    
    @pytest.mark.performance
    def test_memory_usage_under_load(self):
        """Test memory usage under load."""
        print("🧪 Testing memory usage under load...")
        
        # Get initial memory usage
        initial_metrics = self.get_system_metrics()
        print(f"   📊 Initial system metrics:")
        print(f"      CPU: {initial_metrics['cpu_percent']:.1f}%")
        print(f"      Memory: {initial_metrics['memory_percent']:.1f}%")
        print(f"      Available Memory: {initial_metrics['memory_available']:.1f} GB")
        
        # Create load
        num_requests = 20
        request_data = {
            "api_key": self.api_key,
            "model": "gpt-3.5-turbo",
            "batch_size": 1
        }
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(
                    self.make_request,
                    f"{self.api_gateway_url}/prompt-injection/start",
                    "POST",
                    request_data,
                    5  # Shorter timeout for load testing
                )
                for _ in range(num_requests)
            ]
            
            # Monitor memory during execution
            memory_samples = []
            for _ in range(10):  # Sample 10 times
                time.sleep(0.5)
                metrics = self.get_system_metrics()
                memory_samples.append(metrics['memory_percent'])
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Get final memory usage
        final_metrics = self.get_system_metrics()
        max_memory = max(memory_samples) if memory_samples else final_metrics['memory_percent']
        
        print(f"   📊 Memory usage under load:")
        print(f"      Initial Memory: {initial_metrics['memory_percent']:.1f}%")
        print(f"      Max Memory: {max_memory:.1f}%")
        print(f"      Final Memory: {final_metrics['memory_percent']:.1f}%")
        print(f"      Total time: {total_time:.2f}s")
        
        # Memory usage should not exceed reasonable limits
        assert max_memory < 90.0, f"Memory usage too high: {max_memory:.1f}%"
        assert final_metrics['memory_percent'] < 85.0, f"Final memory usage too high: {final_metrics['memory_percent']:.1f}%"
    
    @pytest.mark.performance
    def test_response_time_consistency(self):
        """Test response time consistency across multiple requests."""
        print("🧪 Testing response time consistency...")
        
        num_requests = 10
        response_times = []
        
        for i in range(num_requests):
            success, response_time, status_code = self.make_request(f"{self.api_gateway_url}/health")
            
            if success and status_code == 200:
                response_times.append(response_time)
                print(f"   Request {i+1}: {response_time:.3f}s")
            else:
                print(f"   Request {i+1}: Failed ({status_code})")
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            std_deviation = statistics.stdev(response_times) if len(response_times) > 1 else 0
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            print(f"   📊 Response time statistics:")
            print(f"      Average: {avg_response_time:.3f}s")
            print(f"      Std Dev: {std_deviation:.3f}s")
            print(f"      Max: {max_response_time:.3f}s")
            print(f"      Min: {min_response_time:.3f}s")
            
            # Consistency requirements
            assert std_deviation < 1.0, f"Response time too inconsistent: {std_deviation:.3f}s"
            assert max_response_time < 3.0, f"Max response time too high: {max_response_time:.3f}s"
            assert avg_response_time < 1.5, f"Average response time too high: {avg_response_time:.3f}s"
        else:
            pytest.skip("No successful requests to analyze")
    
    @pytest.mark.performance
    def test_throughput_under_load(self):
        """Test throughput under load."""
        print("🧪 Testing throughput under load...")
        
        num_requests = 50
        request_data = {
            "api_key": self.api_key,
            "model": "gpt-3.5-turbo",
            "batch_size": 1
        }
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [
                executor.submit(
                    self.make_request,
                    f"{self.api_gateway_url}/prompt-injection/start",
                    "POST",
                    request_data,
                    5  # Shorter timeout for throughput testing
                )
                for _ in range(num_requests)
            ]
            
            results = []
            for future in as_completed(futures):
                success, response_time, status_code = future.result()
                results.append((success, response_time, status_code))
        
        end_time = time.time()
        total_time = end_time - start_time
        
        successful_requests = [r for r in results if r[0] and r[2] in [200, 400, 500, 503]]
        throughput = len(successful_requests) / total_time if total_time > 0 else 0
        
        print(f"   📊 Throughput test results:")
        print(f"      Total requests: {num_requests}")
        print(f"      Successful requests: {len(successful_requests)}")
        print(f"      Total time: {total_time:.2f}s")
        print(f"      Throughput: {throughput:.2f} requests/second")
        
        # Throughput requirements
        assert throughput > 0, "No successful requests"
        assert len(successful_requests) >= num_requests * 0.7, f"Too many failed requests: {len(successful_requests)}/{num_requests}"
    
    @pytest.mark.performance
    def test_system_resource_usage(self):
        """Test system resource usage during operations."""
        print("🧪 Testing system resource usage...")
        
        # Monitor system resources
        initial_metrics = self.get_system_metrics()
        
        # Perform operations
        num_operations = 10
        for i in range(num_operations):
            self.make_request(f"{self.api_gateway_url}/health")
            time.sleep(0.1)
        
        final_metrics = self.get_system_metrics()
        
        print(f"   📊 System resource usage:")
        print(f"      Initial CPU: {initial_metrics['cpu_percent']:.1f}%")
        print(f"      Final CPU: {final_metrics['cpu_percent']:.1f}%")
        print(f"      Initial Memory: {initial_metrics['memory_percent']:.1f}%")
        print(f"      Final Memory: {final_metrics['memory_percent']:.1f}%")
        print(f"      Available Memory: {final_metrics['memory_available']:.1f} GB")
        
        # Resource usage should be reasonable
        assert final_metrics['cpu_percent'] < 80.0, f"CPU usage too high: {final_metrics['cpu_percent']:.1f}%"
        assert final_metrics['memory_percent'] < 85.0, f"Memory usage too high: {final_metrics['memory_percent']:.1f}%"
        assert final_metrics['memory_available'] > 1.0, f"Insufficient available memory: {final_metrics['memory_available']:.1f} GB"


class TestStressPerformance:
    """Stress testing for the LLMShield platform."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.api_gateway_url = "http://localhost:8000"
        self.api_key = "sk-test123456789"
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_high_concurrency_stress(self):
        """Test system under high concurrency stress."""
        print("🧪 Testing high concurrency stress...")
        
        num_threads = 50
        requests_per_thread = 5
        
        def stress_worker(thread_id: int):
            """Worker function for stress testing."""
            results = []
            for i in range(requests_per_thread):
                success, response_time, status_code = self.make_request(f"{self.api_gateway_url}/health")
                results.append((thread_id, i, success, response_time, status_code))
                time.sleep(0.1)  # Small delay between requests
            return results
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(stress_worker, i) for i in range(num_threads)]
            
            all_results = []
            for future in as_completed(futures):
                results = future.result()
                all_results.extend(results)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        successful_requests = [r for r in all_results if r[2]]
        response_times = [r[3] for r in successful_requests]
        
        print(f"   📊 High concurrency stress test:")
        print(f"      Threads: {num_threads}")
        print(f"      Requests per thread: {requests_per_thread}")
        print(f"      Total requests: {len(all_results)}")
        print(f"      Successful requests: {len(successful_requests)}")
        print(f"      Total time: {total_time:.2f}s")
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            
            print(f"      Avg response time: {avg_response_time:.3f}s")
            print(f"      Max response time: {max_response_time:.3f}s")
            
            # Stress test requirements
            assert len(successful_requests) >= len(all_results) * 0.8, f"Too many failed requests: {len(successful_requests)}/{len(all_results)}"
            assert avg_response_time < 5.0, f"Average response time too high under stress: {avg_response_time:.3f}s"
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_sustained_load_stress(self):
        """Test system under sustained load."""
        print("🧪 Testing sustained load stress...")
        
        duration_seconds = 30  # 30 seconds of sustained load
        requests_per_second = 5
        
        start_time = time.time()
        request_count = 0
        successful_requests = 0
        response_times = []
        
        while time.time() - start_time < duration_seconds:
            batch_start = time.time()
            
            # Send batch of requests
            with ThreadPoolExecutor(max_workers=requests_per_second) as executor:
                futures = [
                    executor.submit(self.make_request, f"{self.api_gateway_url}/health")
                    for _ in range(requests_per_second)
                ]
                
                for future in as_completed(futures):
                    success, response_time, status_code = future.result()
                    request_count += 1
                    if success:
                        successful_requests += 1
                        response_times.append(response_time)
            
            # Wait for next second
            batch_time = time.time() - batch_start
            if batch_time < 1.0:
                time.sleep(1.0 - batch_time)
        
        total_time = time.time() - start_time
        throughput = request_count / total_time if total_time > 0 else 0
        
        print(f"   📊 Sustained load stress test:")
        print(f"      Duration: {total_time:.2f}s")
        print(f"      Total requests: {request_count}")
        print(f"      Successful requests: {successful_requests}")
        print(f"      Throughput: {throughput:.2f} requests/second")
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            print(f"      Avg response time: {avg_response_time:.3f}s")
            
            # Sustained load requirements
            assert successful_requests >= request_count * 0.8, f"Too many failed requests: {successful_requests}/{request_count}"
            assert throughput > 2.0, f"Throughput too low: {throughput:.2f} requests/second"
            assert avg_response_time < 3.0, f"Average response time too high: {avg_response_time:.3f}s"
    
    def make_request(self, url: str, method: str = "GET", data: Dict = None, timeout: int = 10) -> Tuple[bool, float, int]:
        """Make a request and return success, response_time, status_code."""
        start_time = time.time()
        try:
            if method == "GET":
                response = requests.get(url, timeout=timeout)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=timeout)
            elif method == "DELETE":
                response = requests.delete(url, timeout=timeout)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return True, response_time, response.status_code
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            return False, response_time, 0

