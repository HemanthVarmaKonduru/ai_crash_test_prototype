"""
Main analytics service for tracking and aggregating test metrics.
"""
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from .model_pricing import ModelPricing
from .token_counter import extract_token_usage, aggregate_token_usage
from .persistence import AnalyticsPersistence


class AnalyticsService:
    """Main service for analytics tracking and aggregation."""
    
    def __init__(self, persistence: Optional[AnalyticsPersistence] = None):
        """
        Initialize analytics service.
        
        Args:
            persistence: Persistence layer instance (creates default if None)
        """
        self.persistence = persistence or AnalyticsPersistence()
        self._in_memory_runs: Dict[str, Dict[str, Any]] = {}
    
    async def record_test_run(
        self,
        test_id: str,
        test_type: str,
        session: Dict[str, Any],
        captured_responses: List[Dict[str, Any]],
        evaluated_responses: List[Dict[str, Any]],
        target_model: str,
        judge_model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Record analytics for a completed test run.
        
        Args:
            test_id: Unique test identifier
            test_type: Type of test (prompt_injection, jailbreak, etc.)
            session: Test session data
            captured_responses: List of captured API responses
            evaluated_responses: List of evaluated responses
            target_model: Model being tested
            judge_model: Model used for evaluation (if different)
            
        Returns:
            Analytics data for the test run
        """
        # Extract metrics from responses
        target_tokens = self._extract_tokens_from_responses(
            captured_responses, "target_model"
        )
        
        judge_tokens = self._extract_tokens_from_responses(
            evaluated_responses, "judge_model"
        )
        
        # Calculate costs
        target_cost = ModelPricing.calculate_cost(
            target_model,
            target_tokens["input_tokens"],
            target_tokens["output_tokens"]
        )
        
        judge_cost = 0.0
        if judge_model and judge_tokens["total_tokens"] > 0:
            judge_cost = ModelPricing.calculate_cost(
                judge_model,
                judge_tokens["input_tokens"],
                judge_tokens["output_tokens"]
            )
        
        # Extract time metrics
        total_execution_time = session.get("results", {}).get("total_execution_time", 0)
        if not total_execution_time and session.get("start_time") and session.get("end_time"):
            start = datetime.fromisoformat(session["start_time"])
            end = datetime.fromisoformat(session["end_time"])
            total_execution_time = (end - start).total_seconds()
        
        avg_response_time = session.get("results", {}).get("performance_metrics", {}).get(
            "average_response_time", 0
        )
        
        # Calculate average evaluation time
        eval_times = [r.get("evaluation_time", 0) for r in evaluated_responses if r.get("evaluation_time")]
        avg_evaluation_time = sum(eval_times) / len(eval_times) if eval_times else 0
        
        # Count prompts and API calls
        total_prompts = len(captured_responses)
        successful_captures = len([r for r in captured_responses if r.get("capture_success", True)])
        failed_captures = total_prompts - successful_captures
        successful_evaluations = len(evaluated_responses)
        
        total_api_calls = len(captured_responses)
        # Add judge model API calls if they exist separately
        if judge_model:
            # Evaluation might make additional API calls
            total_api_calls += len(evaluated_responses)
        
        # Build analytics record
        analytics_data = {
            "test_id": test_id,
            "test_type": test_type,
            "timestamp": session.get("start_time", datetime.now().isoformat()),
            "completed_at": session.get("end_time", datetime.now().isoformat()),
            "status": session.get("status", "completed"),
            "metrics": {
                "tokens": {
                    "target_model": {
                        "model": target_model,
                        "input_tokens": target_tokens["input_tokens"],
                        "output_tokens": target_tokens["output_tokens"],
                        "total_tokens": target_tokens["total_tokens"],
                    },
                    "judge_model": {
                        "model": judge_model or "none",
                        "input_tokens": judge_tokens["input_tokens"],
                        "output_tokens": judge_tokens["output_tokens"],
                        "total_tokens": judge_tokens["total_tokens"],
                    },
                    "total": target_tokens["total_tokens"] + judge_tokens["total_tokens"],
                },
                "cost": {
                    "target_model": round(target_cost, 6),
                    "judge_model": round(judge_cost, 6),
                    "total": round(target_cost + judge_cost, 6),
                    "per_prompt": round((target_cost + judge_cost) / total_prompts, 6) if total_prompts > 0 else 0,
                },
                "time": {
                    "total_execution": round(total_execution_time, 2),
                    "average_response": round(avg_response_time, 2),
                    "average_evaluation": round(avg_evaluation_time, 2),
                    "per_prompt": round(total_execution_time / total_prompts, 2) if total_prompts > 0 else 0,
                },
                "prompts": {
                    "total": total_prompts,
                    "successful_captures": successful_captures,
                    "failed_captures": failed_captures,
                    "successful_evaluations": successful_evaluations,
                    "failed_evaluations": total_prompts - successful_evaluations,
                },
                "performance": {
                    "total_api_calls": total_api_calls,
                    "success_rate": round(successful_captures / total_prompts, 4) if total_prompts > 0 else 0,
                    "failure_rate": round(failed_captures / total_prompts, 4) if total_prompts > 0 else 0,
                },
            },
            "results_summary": {
                "detection_rate": session.get("results", {}).get("detection_rate", 0),
                "robustness_rate": session.get("results", {}).get("robustness_rate", 0),
                "successful_resistances": session.get("results", {}).get("successful_resistances", 0),
                "failed_resistances": session.get("results", {}).get("failed_resistances", 0),
                "failed_attacks": session.get("results", {}).get("failed_attacks", 0),
                "failed_extractions": session.get("results", {}).get("failed_extractions", 0),
            },
        }
        
        # Store in memory
        self._in_memory_runs[test_id] = analytics_data
        
        # Persist to disk
        self.persistence.save_test_run(analytics_data)
        
        # Update aggregated analytics
        await self._update_aggregated()
        
        return analytics_data
    
    def _extract_tokens_from_responses(
        self,
        responses: List[Dict[str, Any]],
        model_type: str
    ) -> Dict[str, int]:
        """
        Extract token usage from responses.
        
        Args:
            responses: List of response dictionaries
            model_type: Type of model (target_model or judge_model)
            
        Returns:
            Aggregated token counts
        """
        token_records = []
        
        for response in responses:
            # Try to get token usage from response
            if "token_usage" in response:
                token_records.append(response["token_usage"])
            elif "usage" in response:
                usage = response["usage"]
                token_records.append({
                    "input_tokens": usage.get("prompt_tokens", 0) or usage.get("input_tokens", 0),
                    "output_tokens": usage.get("completion_tokens", 0) or usage.get("output_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                })
            elif "input_tokens" in response or "output_tokens" in response:
                token_records.append({
                    "input_tokens": response.get("input_tokens", 0),
                    "output_tokens": response.get("output_tokens", 0),
                    "total_tokens": response.get("total_tokens", 0),
                })
        
        if token_records:
            return aggregate_token_usage(token_records)
        else:
            return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    
    async def _update_aggregated(self) -> None:
        """Update aggregated analytics from all test runs."""
        test_runs = self.persistence.load_test_runs()
        
        # Initialize aggregated data
        aggregated = {
            "summary": {
                "total_tests": len(test_runs),
                "total_prompts": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "average_cost_per_test": 0.0,
                "average_tokens_per_test": 0,
                "average_time_per_test": 0.0,
            },
            "by_module": {},
        }
        
        if not test_runs:
            # No test runs yet, save empty aggregated data
            self.persistence.save_aggregated(aggregated)
            return
        
        # Aggregate metrics
        for test_run in test_runs:
            metrics = test_run.get("metrics", {})
            
            # Update summary
            aggregated["summary"]["total_prompts"] += metrics.get("prompts", {}).get("total", 0)
            aggregated["summary"]["total_tokens"] += metrics.get("tokens", {}).get("total", 0)
            aggregated["summary"]["total_cost"] += metrics.get("cost", {}).get("total", 0)
            
            total_time = metrics.get("time", {}).get("total_execution", 0)
            aggregated["summary"]["average_time_per_test"] += total_time
            
            # Update by module
            test_type = test_run.get("test_type", "unknown")
            if test_type not in aggregated["by_module"]:
                aggregated["by_module"][test_type] = {
                    "total_tests": 0,
                    "total_prompts": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "total_time": 0.0,
                    "successful": 0,
                    "failures": 0,
                }
            
            module_stats = aggregated["by_module"][test_type]
            module_stats["total_tests"] += 1
            module_stats["total_prompts"] += metrics.get("prompts", {}).get("total", 0)
            module_stats["total_tokens"] += metrics.get("tokens", {}).get("total", 0)
            module_stats["total_cost"] += metrics.get("cost", {}).get("total", 0)
            module_stats["total_time"] += total_time
            
            # Count successes/failures
            results = test_run.get("results_summary", {})
            successful = results.get("successful_resistances", 0)
            failures = (
                results.get("failed_resistances", 0) +
                results.get("failed_attacks", 0) +
                results.get("failed_extractions", 0)
            )
            module_stats["successful"] += successful
            module_stats["failures"] += failures
        
        # Calculate averages
        if aggregated["summary"]["total_tests"] > 0:
            aggregated["summary"]["average_cost_per_test"] = (
                aggregated["summary"]["total_cost"] / aggregated["summary"]["total_tests"]
            )
            aggregated["summary"]["average_tokens_per_test"] = (
                aggregated["summary"]["total_tokens"] // aggregated["summary"]["total_tests"]
            )
            aggregated["summary"]["average_time_per_test"] = (
                aggregated["summary"]["average_time_per_test"] / aggregated["summary"]["total_tests"]
            )
        
        # Calculate module averages
        for module_type, stats in aggregated["by_module"].items():
            if stats["total_tests"] > 0:
                stats["average_cost"] = stats["total_cost"] / stats["total_tests"]
                stats["average_tokens"] = stats["total_tokens"] // stats["total_tests"]
                stats["average_time"] = stats["total_time"] / stats["total_tests"]
                stats["avg_response_time"] = (
                    stats["total_time"] / stats["total_prompts"] if stats["total_prompts"] > 0 else 0
                )
        
        # Save aggregated data
        self.persistence.save_aggregated(aggregated)
    
    def get_test_analytics(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Get analytics for a specific test run.
        
        Args:
            test_id: Test ID
            
        Returns:
            Analytics data or None
        """
        # Check in-memory first
        if test_id in self._in_memory_runs:
            return self._in_memory_runs[test_id]
        
        # Check persistence
        return self.persistence.get_test_run(test_id)
    
    def get_aggregated_analytics(self) -> Dict[str, Any]:
        """
        Get aggregated analytics across all test runs.
        
        Returns:
            Aggregated analytics data
        """
        return self.persistence.load_aggregated()
    
    def get_module_analytics(self, module_type: str) -> List[Dict[str, Any]]:
        """
        Get analytics for a specific module type.
        
        Args:
            module_type: Module type (prompt_injection, jailbreak, etc.)
            
        Returns:
            List of test run analytics for that module
        """
        return self.persistence.get_module_stats(module_type)

