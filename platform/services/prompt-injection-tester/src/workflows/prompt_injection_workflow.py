"""
Prompt Injection Workflow using LangGraph for multi-agent orchestration.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../libs"))

from workflows.base_workflow import BaseWorkflow, WorkflowState, WorkflowStatus
from agents.validation_agent import PromptInjectionValidationAgent
from agents.test_execution_agent import PromptInjectionTestExecutionAgent
from agents.evaluation_agent import PromptInjectionEvaluationAgent
from agents.report_analysis_agent import PromptInjectionReportAnalysisAgent
from typing import Dict, Any, List

class PromptInjectionWorkflow(BaseWorkflow):
    """Workflow for prompt injection testing using multi-agent system."""
    
    def __init__(self, config: Dict[str, Any], workflow_id: str):
        super().__init__(config, workflow_id)
        self.module_type = "prompt_injection"
        
        # Initialize agents
        self.validation_agent = PromptInjectionValidationAgent(config, "validation")
        self.test_execution_agent = PromptInjectionTestExecutionAgent(config, "test_execution")
        self.evaluation_agent = PromptInjectionEvaluationAgent(config, "evaluation")
        self.report_analysis_agent = PromptInjectionReportAnalysisAgent(config, "report_analysis")
        
        # Register agents
        self.register_agent("validation", self.validation_agent)
        self.register_agent("test_execution", self.test_execution_agent)
        self.register_agent("evaluation", self.evaluation_agent)
        self.register_agent("report_analysis", self.report_analysis_agent)
    
    def get_workflow_steps(self) -> List[str]:
        """Define prompt injection workflow steps."""
        return [
            "validation",
            "test_execution", 
            "evaluation",
            "report_analysis"
        ]
    
    async def execute_step(self, step_name: str, state: WorkflowState) -> WorkflowState:
        """Execute a specific workflow step."""
        try:
            if step_name == "validation":
                return await self._execute_validation_step(state)
            elif step_name == "test_execution":
                return await self._execute_test_execution_step(state)
            elif step_name == "evaluation":
                return await self._execute_evaluation_step(state)
            elif step_name == "report_analysis":
                return await self._execute_report_analysis_step(state)
            else:
                raise ValueError(f"Unknown step: {step_name}")
                
        except Exception as e:
            self.logger.error(f"Step {step_name} execution failed: {str(e)}")
            state.errors.append(f"Step {step_name} failed: {str(e)}")
            state.status = WorkflowStatus.FAILED
            return state
    
    async def _execute_validation_step(self, state: WorkflowState) -> WorkflowState:
        """Execute validation step."""
        self.logger.info("Executing validation step")
        
        # Prepare validation data
        validation_data = {
            "api_key": state.data.get("api_key"),
            "model": state.data.get("model"),
            "user_id": state.data.get("user_id"),
            "dataset_path": state.data.get("dataset_path"),
            "batch_size": state.data.get("batch_size"),
            "max_tokens": state.data.get("max_tokens"),
            "temperature": state.data.get("temperature")
        }
        
        # Execute validation
        validation_result = await self.validation_agent.execute(validation_data)
        
        if not validation_result.success:
            state.errors.append(f"Validation failed: {validation_result.error}")
            state.status = WorkflowStatus.FAILED
            return state
        
        # Update state with validation results
        state.data.update({
            "validation_result": validation_result.data,
            "validation_successful": True
        })
        
        self.logger.info("Validation step completed successfully")
        return state
    
    async def _execute_test_execution_step(self, state: WorkflowState) -> WorkflowState:
        """Execute test execution step."""
        self.logger.info("Executing test execution step")
        
        # Prepare test execution data
        test_execution_data = {
            "session_id": state.data.get("session_id"),
            "api_key": state.data.get("api_key"),
            "model": state.data.get("model"),
            "user_id": state.data.get("user_id"),
            "dataset_path": state.data.get("dataset_path"),
            "batch_size": state.data.get("batch_size"),
            "max_tokens": state.data.get("max_tokens"),
            "temperature": state.data.get("temperature")
        }
        
        # Execute test execution
        execution_result = await self.test_execution_agent.execute(test_execution_data)
        
        if not execution_result.success:
            state.errors.append(f"Test execution failed: {execution_result.error}")
            state.status = WorkflowStatus.FAILED
            return state
        
        # Update state with test execution results
        state.data.update({
            "test_execution_result": execution_result.data,
            "test_results": execution_result.data.get("results", []),
            "test_execution_successful": True
        })
        
        self.logger.info("Test execution step completed successfully")
        return state
    
    async def _execute_evaluation_step(self, state: WorkflowState) -> WorkflowState:
        """Execute evaluation step."""
        self.logger.info("Executing evaluation step")
        
        # Prepare evaluation data
        evaluation_data = {
            "test_results": state.data.get("test_results", []),
            "evaluation_type": "prompt_injection",
            "session_id": state.data.get("session_id"),
            "user_id": state.data.get("user_id")
        }
        
        # Execute evaluation
        evaluation_result = await self.evaluation_agent.execute(evaluation_data)
        
        if not evaluation_result.success:
            state.errors.append(f"Evaluation failed: {evaluation_result.error}")
            state.status = WorkflowStatus.FAILED
            return state
        
        # Update state with evaluation results
        state.data.update({
            "evaluation_result": evaluation_result.data,
            "evaluated_results": evaluation_result.data.get("evaluated_results", []),
            "evaluation_metrics": evaluation_result.data.get("metrics", {}),
            "evaluation_successful": True
        })
        
        self.logger.info("Evaluation step completed successfully")
        return state
    
    async def _execute_report_analysis_step(self, state: WorkflowState) -> WorkflowState:
        """Execute report analysis step."""
        self.logger.info("Executing report analysis step")
        
        # Prepare report analysis data
        report_analysis_data = {
            "evaluated_results": state.data.get("evaluated_results", []),
            "metrics": state.data.get("evaluation_metrics", {}),
            "evaluation_type": "prompt_injection",
            "session_id": state.data.get("session_id"),
            "user_id": state.data.get("user_id")
        }
        
        # Execute report analysis
        report_analysis_result = await self.report_analysis_agent.execute(report_analysis_data)
        
        if not report_analysis_result.success:
            state.errors.append(f"Report analysis failed: {report_analysis_result.error}")
            state.status = WorkflowStatus.FAILED
            return state
        
        # Update state with report analysis results
        state.data.update({
            "report_analysis_result": report_analysis_result.data,
            "final_report": report_analysis_result.data.get("report_data", {}),
            "ui_data": report_analysis_result.data.get("ui_data", {}),
            "report_analysis_successful": True
        })
        
        self.logger.info("Report analysis step completed successfully")
        return state
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """Get prompt injection workflow information."""
        base_info = super().get_workflow_info()
        base_info.update({
            "module_type": self.module_type,
            "workflow_type": "prompt_injection_multi_agent",
            "agents": {
                "validation": "PromptInjectionValidationAgent",
                "test_execution": "PromptInjectionTestExecutionAgent", 
                "evaluation": "PromptInjectionEvaluationAgent",
                "report_analysis": "PromptInjectionReportAnalysisAgent"
            }
        })
        return base_info

