"""
Base Agent class for all LLMShield agents.
Provides common functionality and interface for all agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AgentResult:
    """Standard result structure for all agents."""
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    confidence: float = 0.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class BaseAgent(ABC):
    """
    Base class for all LLMShield agents.
    Provides common functionality and interface.
    """
    
    def __init__(self, config: Dict[str, Any], agent_id: str):
        self.config = config
        self.agent_id = agent_id
        self.status = AgentStatus.IDLE
        self.logger = logging.getLogger(f"{__name__}.{agent_id}")
        
    @abstractmethod
    async def execute(self, state: Dict[str, Any]) -> AgentResult:
        """
        Execute the agent's main functionality.
        
        Args:
            state: Current workflow state
            
        Returns:
            AgentResult: Execution result
        """
        pass
    
    @abstractmethod
    async def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data for the agent.
        
        Args:
            data: Input data to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        pass
    
    async def pre_execute(self, state: Dict[str, Any]) -> bool:
        """
        Pre-execution setup and validation.
        
        Args:
            state: Current workflow state
            
        Returns:
            bool: True if ready to execute, False otherwise
        """
        self.status = AgentStatus.RUNNING
        self.logger.info(f"Agent {self.agent_id} starting execution")
        return True
    
    async def post_execute(self, result: AgentResult) -> AgentResult:
        """
        Post-execution cleanup and result processing.
        
        Args:
            result: Agent execution result
            
        Returns:
            AgentResult: Processed result
        """
        if result.success:
            self.status = AgentStatus.COMPLETED
            self.logger.info(f"Agent {self.agent_id} completed successfully")
        else:
            self.status = AgentStatus.FAILED
            self.logger.error(f"Agent {self.agent_id} failed: {result.error}")
        
        return result
    
    async def handle_error(self, error: Exception) -> AgentResult:
        """
        Handle agent execution errors.
        
        Args:
            error: Exception that occurred
            
        Returns:
            AgentResult: Error result
        """
        self.status = AgentStatus.FAILED
        self.logger.error(f"Agent {self.agent_id} error: {str(error)}")
        
        return AgentResult(
            success=False,
            data={},
            error=str(error),
            confidence=0.0,
            metadata={"agent_id": self.agent_id, "error_type": type(error).__name__}
        )
    
    def get_status(self) -> AgentStatus:
        """Get current agent status."""
        return self.status
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "config": self.config
        }

