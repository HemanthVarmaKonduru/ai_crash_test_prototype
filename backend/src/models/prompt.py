"""
Prompt data models
"""
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import uuid


class PromptCategory(str, Enum):
    """Categories for crash test prompts"""
    SAFETY = "safety"
    BIAS = "bias"
    PRIVACY = "privacy"
    GENERAL = "general"
    HARM = "harm"
    ILLEGAL = "illegal"


class PromptDifficulty(str, Enum):
    """Difficulty levels for prompts"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXTREME = "extreme"


class ExpectedBehavior(str, Enum):
    """Expected model behaviors"""
    REJECT = "reject"
    NEUTRALIZE = "neutralize"
    SAFE_EXPLANATION = "safe_explanation"
    REFUSE = "refuse"
    REDIRECT = "redirect"


class Prompt(BaseModel):
    """Crash test prompt model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    category: PromptCategory
    difficulty: PromptDifficulty
    expected_behavior: ExpectedBehavior
    source: str = "unknown"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class PromptBatch(BaseModel):
    """Batch of prompts for processing"""
    prompts: list[Prompt]
    batch_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str = "unknown"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def __len__(self) -> int:
        return len(self.prompts)
    
    def __iter__(self):
        return iter(self.prompts)
    
    def __getitem__(self, index):
        return self.prompts[index]


