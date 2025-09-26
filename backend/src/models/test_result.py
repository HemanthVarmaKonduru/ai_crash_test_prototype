"""
Test result data models
"""
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from .prompt import PromptCategory, PromptDifficulty


class TestStatus(str, Enum):
    """Test result status"""
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    ERROR = "ERROR"


class TestResult(BaseModel):
    """Individual test result"""
    id: str
    prompt_id: str
    model_name: str
    model_response: str
    status: TestStatus
    category: Optional[PromptCategory] = None
    difficulty: Optional[PromptDifficulty] = None
    expected_behavior: str
    evaluation_score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True
    
    def get_safety_flags(self) -> Dict[str, bool]:
        """Get safety flags from metadata"""
        if 'flags' in self.metadata:
            return self.metadata['flags']
        return {}
    
    def has_toxicity(self) -> bool:
        """Check if response contains toxicity"""
        flags = self.get_safety_flags()
        return flags.get('toxicity', False)
    
    def has_pii(self) -> bool:
        """Check if response contains PII"""
        flags = self.get_safety_flags()
        return flags.get('pii', False)
    
    def has_bias(self) -> bool:
        """Check if response contains bias"""
        flags = self.get_safety_flags()
        return flags.get('bias', False)
    
    def is_behavior_compliant(self) -> bool:
        """Check if response is behavior compliant"""
        flags = self.get_safety_flags()
        return flags.get('behavior_compliance', False)
    
    def get_evaluator_name(self) -> str:
        """Get the evaluator name from metadata"""
        return self.metadata.get('evaluator', 'unknown')


class TestRun(BaseModel):
    """Complete test run results"""
    run_id: str
    model_name: str
    results: list[TestResult]
    total_tests: int
    passed: int
    failed: int
    unknown: int
    errors: int
    pass_rate: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def __len__(self) -> int:
        return len(self.results)
    
    def __iter__(self):
        return iter(self.results)
    
    def get_safety_flags_summary(self) -> Dict[str, Any]:
        """Get summary of safety flags across all results"""
        if not self.results:
            return {
                "total_tests": 0,
                "toxicity_detected": 0,
                "pii_detected": 0,
                "bias_detected": 0,
                "behavior_compliant": 0,
                "flags_percentage": {
                    "toxicity": 0.0,
                    "pii": 0.0,
                    "bias": 0.0,
                    "behavior_compliance": 0.0
                }
            }
        
        total = len(self.results)
        toxicity_count = sum(1 for r in self.results if r.has_toxicity())
        pii_count = sum(1 for r in self.results if r.has_pii())
        bias_count = sum(1 for r in self.results if r.has_bias())
        compliance_count = sum(1 for r in self.results if r.is_behavior_compliant())
        
        return {
            "total_tests": total,
            "toxicity_detected": toxicity_count,
            "pii_detected": pii_count,
            "bias_detected": bias_count,
            "behavior_compliant": compliance_count,
            "flags_percentage": {
                "toxicity": (toxicity_count / total * 100) if total > 0 else 0.0,
                "pii": (pii_count / total * 100) if total > 0 else 0.0,
                "bias": (bias_count / total * 100) if total > 0 else 0.0,
                "behavior_compliance": (compliance_count / total * 100) if total > 0 else 0.0
            }
        }


class TestSummary(BaseModel):
    """Summary statistics for test results"""
    total_tests: int
    passed: int
    failed: int
    unknown: int
    errors: int
    pass_rate: float
    category_stats: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    difficulty_stats: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    model_stats: Dict[str, Dict[str, int]] = Field(default_factory=dict)


