"""
Storage interface for data persistence
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from ..models.prompt import Prompt, PromptBatch
from ..models.test_result import TestResult, TestRun


class StorageInterface(ABC):
    """Abstract interface for data storage"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    async def save_prompts(self, prompts: PromptBatch) -> bool:
        """Save a batch of prompts"""
        pass
    
    @abstractmethod
    async def load_prompts(self, filters: Optional[Dict[str, Any]] = None) -> PromptBatch:
        """Load prompts with optional filtering"""
        pass
    
    @abstractmethod
    async def save_test_results(self, test_run: TestRun) -> bool:
        """Save test results"""
        pass
    
    @abstractmethod
    async def load_test_results(self, run_id: Optional[str] = None) -> List[TestRun]:
        """Load test results"""
        pass
    
    @abstractmethod
    async def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check storage health"""
        pass


