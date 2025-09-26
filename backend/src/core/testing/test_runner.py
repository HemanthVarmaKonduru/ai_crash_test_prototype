"""
Test runner for executing crash tests
"""
import asyncio
from typing import List, Optional, Dict, Any
from src.models.prompt import Prompt, PromptBatch
from src.models.test_result import TestResult, TestRun, TestStatus
from src.interfaces.model_interface import ModelInterface
from src.interfaces.evaluator_interface import EvaluatorInterface


class TestRunner:
    """Runs crash tests against AI models"""
    
    def __init__(
        self, 
        model: ModelInterface, 
        evaluator: EvaluatorInterface
    ):
        self.model = model
        self.evaluator = evaluator
    
    async def run_single_test(self, prompt: Prompt) -> TestResult:
        """Run a single test case"""
        try:
            # Get model response
            response = await self.model.test_prompt(prompt)
            
            # Evaluate response
            result = self.evaluator.evaluate_response(
                prompt, response, prompt.expected_behavior
            )
            
            # Set model name
            result.model_name = self.model.name
            
            return result
            
        except Exception as e:
            return TestResult(
                id=f"{prompt.id}_error",
                prompt_id=prompt.id,
                model_name=self.model.name,
                model_response=f"Error: {str(e)}",
                status=TestStatus.ERROR,
                category=prompt.category,
                difficulty=prompt.difficulty,
                expected_behavior=prompt.expected_behavior.value,
                metadata={"error": str(e)}
            )
    
    async def run_batch_tests(
        self, 
        prompts: PromptBatch, 
        max_concurrent: int = 5
    ) -> TestRun:
        """Run tests on a batch of prompts with concurrency control"""
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def run_with_semaphore(prompt: Prompt) -> TestResult:
            async with semaphore:
                return await self.run_single_test(prompt)
        
        # Run tests concurrently
        tasks = [run_with_semaphore(prompt) for prompt in prompts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        test_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Create error result
                error_result = TestResult(
                    id=f"{prompts[i].id}_error",
                    prompt_id=prompts[i].id,
                    model_name=self.model.name,
                    model_response=f"Error: {str(result)}",
                    status=TestStatus.ERROR,
                    category=prompts[i].category,
                    difficulty=prompts[i].difficulty,
                    expected_behavior=prompts[i].expected_behavior.value,
                    metadata={"error": str(result)}
                )
                test_results.append(error_result)
            else:
                test_results.append(result)
        
        # Create test run
        return self._create_test_run(test_results)
    
    def _create_test_run(self, results: List[TestResult]) -> TestRun:
        """Create a test run from results"""
        total = len(results)
        passed = sum(1 for r in results if r.status == TestStatus.PASS)
        failed = sum(1 for r in results if r.status == TestStatus.FAIL)
        unknown = sum(1 for r in results if r.status == TestStatus.UNKNOWN)
        errors = sum(1 for r in results if r.status == TestStatus.ERROR)
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        return TestRun(
            run_id=f"run_{self.model.name}_{len(results)}",
            model_name=self.model.name,
            results=results,
            total_tests=total,
            passed=passed,
            failed=failed,
            unknown=unknown,
            errors=errors,
            pass_rate=pass_rate,
            metadata={
                "model": self.model.get_model_info(),
                "evaluator": self.evaluator.get_evaluation_criteria()
            }
        )
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of model and evaluator"""
        model_healthy = await self.model.health_check()
        evaluator_healthy = self.evaluator.validate_config()
        
        return {
            "model": model_healthy,
            "evaluator": evaluator_healthy,
            "overall": model_healthy and evaluator_healthy
        }
