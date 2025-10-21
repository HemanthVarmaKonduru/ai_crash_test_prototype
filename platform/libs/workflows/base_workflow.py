"""
Base Workflow class using LangGraph for multi-agent orchestration.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import asyncio
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class WorkflowState:
    """Workflow state container."""
    session_id: str
    user_id: str
    status: WorkflowStatus
    current_step: str
    data: Dict[str, Any]
    errors: List[str]
    metadata: Dict[str, Any]

class BaseWorkflow(ABC):
    """
    Base workflow class for multi-agent orchestration using LangGraph concepts.
    """
    
    def __init__(self, config: Dict[str, Any], workflow_id: str):
        self.config = config
        self.workflow_id = workflow_id
        self.status = WorkflowStatus.PENDING
        self.logger = logging.getLogger(f"{__name__}.{workflow_id}")
        self.agents = {}
        self.state_history = []
        
    @abstractmethod
    def get_workflow_steps(self) -> List[str]:
        """
        Define workflow execution steps.
        
        Returns:
            List[str]: Ordered list of step names
        """
        pass
    
    @abstractmethod
    async def execute_step(self, step_name: str, state: WorkflowState) -> WorkflowState:
        """
        Execute a specific workflow step.
        
        Args:
            step_name: Name of the step to execute
            state: Current workflow state
            
        Returns:
            WorkflowState: Updated state after step execution
        """
        pass
    
    async def execute(self, initial_state: Dict[str, Any]) -> WorkflowState:
        """
        Execute the complete workflow.
        
        Args:
            initial_state: Initial workflow state
            
        Returns:
            WorkflowState: Final workflow state
        """
        try:
            self.status = WorkflowStatus.RUNNING
            self.logger.info(f"Starting workflow {self.workflow_id}")
            
            # Initialize workflow state
            state = WorkflowState(
                session_id=initial_state.get("session_id"),
                user_id=initial_state.get("user_id"),
                status=WorkflowStatus.RUNNING,
                current_step="initialization",
                data=initial_state,
                errors=[],
                metadata={}
            )
            
            # Execute workflow steps
            steps = self.get_workflow_steps()
            
            for step_name in steps:
                self.logger.info(f"Executing step: {step_name}")
                state.current_step = step_name
                
                try:
                    state = await self.execute_step(step_name, state)
                    self.state_history.append(state)
                    
                    # Check for step failure
                    if state.errors:
                        self.logger.error(f"Step {step_name} failed: {state.errors}")
                        state.status = WorkflowStatus.FAILED
                        break
                        
                except Exception as e:
                    error_msg = f"Step {step_name} execution failed: {str(e)}"
                    self.logger.error(error_msg)
                    state.errors.append(error_msg)
                    state.status = WorkflowStatus.FAILED
                    break
            
            # Finalize workflow
            if state.status == WorkflowStatus.RUNNING:
                state.status = WorkflowStatus.COMPLETED
                self.logger.info(f"Workflow {self.workflow_id} completed successfully")
            else:
                self.logger.error(f"Workflow {self.workflow_id} failed")
            
            self.status = state.status
            return state
            
        except Exception as e:
            self.logger.error(f"Workflow {self.workflow_id} execution failed: {str(e)}")
            return WorkflowState(
                session_id=initial_state.get("session_id"),
                user_id=initial_state.get("user_id"),
                status=WorkflowStatus.FAILED,
                current_step="error",
                data=initial_state,
                errors=[str(e)],
                metadata={}
            )
    
    def register_agent(self, agent_name: str, agent_instance):
        """Register an agent for the workflow."""
        self.agents[agent_name] = agent_instance
        self.logger.info(f"Registered agent: {agent_name}")
    
    def get_agent(self, agent_name: str):
        """Get a registered agent."""
        return self.agents.get(agent_name)
    
    def get_workflow_status(self) -> WorkflowStatus:
        """Get current workflow status."""
        return self.status
    
    def get_state_history(self) -> List[WorkflowState]:
        """Get workflow state history."""
        return self.state_history
    
    def cancel_workflow(self):
        """Cancel the workflow execution."""
        self.status = WorkflowStatus.CANCELLED
        self.logger.info(f"Workflow {self.workflow_id} cancelled")
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """Get workflow information."""
        return {
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "steps": self.get_workflow_steps(),
            "registered_agents": list(self.agents.keys()),
            "state_history_count": len(self.state_history)
        }

