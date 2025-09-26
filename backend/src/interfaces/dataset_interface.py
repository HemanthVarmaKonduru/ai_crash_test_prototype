"""
Dataset interface for data sources
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from ..models.prompt import Prompt, PromptBatch


class DatasetInterface(ABC):
    """Abstract interface for dataset providers"""
    
    def __init__(self, name: str, source: str):
        self.name = name
        self.source = source
    
    @abstractmethod
    async def load_dataset(self, **kwargs) -> PromptBatch:
        """Load a dataset and return a batch of prompts"""
        pass
    
    @abstractmethod
    async def get_dataset_info(self) -> Dict[str, Any]:
        """Get information about the dataset"""
        pass
    
    @abstractmethod
    def supports_filtering(self) -> bool:
        """Check if the dataset supports filtering"""
        pass
    
    @abstractmethod
    async def filter_dataset(
        self, 
        batch: PromptBatch, 
        filters: Dict[str, Any]
    ) -> PromptBatch:
        """Filter the dataset based on criteria"""
        pass
    
    def validate_source(self) -> bool:
        """Validate the data source"""
        return self.source is not None and self.name is not None


