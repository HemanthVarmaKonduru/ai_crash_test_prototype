"""
Evaluator interface for response evaluation
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..models.prompt import Prompt, ExpectedBehavior
from ..models.test_result import TestResult, TestStatus
from ..models.config import EvaluationConfig


class EvaluatorInterface(ABC):
    """Abstract interface for response evaluators"""
    
    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.name = config.evaluator_name
    
    @abstractmethod
    def evaluate_response(
        self, 
        prompt: Prompt, 
        response: str, 
        expected_behavior: ExpectedBehavior
    ) -> TestResult:
        """Evaluate a model response against expected behavior"""
        pass
    
    @abstractmethod
    def get_evaluation_criteria(self) -> Dict[str, Any]:
        """Get the evaluation criteria and rules"""
        pass
    
    @abstractmethod
    def supports_behavior(self, behavior: ExpectedBehavior) -> bool:
        """Check if this evaluator supports the given expected behavior"""
        pass
    
    def get_supported_flags(self) -> Dict[str, str]:
        """Get the flags that this evaluator can detect"""
        return {}
    
    def validate_config(self) -> bool:
        """Validate the evaluator configuration"""
        return self.config.evaluator_name is not None


