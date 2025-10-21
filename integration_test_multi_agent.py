#!/usr/bin/env python3
"""
Comprehensive Integration Test for Multi-Agent System
Tests the complete workflow with real dataset and API calls.
"""

import sys
import os
import json
import asyncio
import time
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add paths
sys.path.insert(0, 'platform/libs/agents')
sys.path.insert(0, 'platform/libs/evaluation')
sys.path.insert(0, 'platform/services/prompt-injection-tester/src')

# Import all agents
from agents.validation_agent import PromptInjectionValidationAgent
from agents.test_execution_agent import PromptInjectionTestExecutionAgent
from agents.evaluation_agent import PromptInjectionEvaluationAgent
from agents.report_analysis_agent import PromptInjectionReportAnalysisAgent

# API Configuration - using new API key for testing
API_KEY = "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"
TARGET_MODEL = "gpt-3.5-turbo"  # Model to test
JUDGE_MODEL = "gpt-4o-mini"     # Model for evaluation

class MultiAgentIntegrationTest:
    """Integration test for the complete multi-agent workflow."""
    
    def __init__(self):
        self.api_key = API_KEY
        self.target_model = TARGET_MODEL
        self.judge_model = JUDGE_MODEL
        self.test_results = []
        self.start_time = None
        self.end_time = None
        
    async def load_test_dataset(self, limit: int = 25) -> List[Dict[str, Any]]:
        """Load the first N samples from the prompt injection dataset."""
        print(f"📊 Loading first {limit} samples from prompt injection dataset...")
        
        try:
            with open('data/prompt_injection.json', 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            
            # Take first N samples
            test_samples = dataset[:limit]
            print(f"✅ Loaded {len(test_samples)} test samples")
            
            # Transform to expected format
            transformed_samples = []
            for sample in test_samples:
                transformed_samples.append({
                    "sample_id": f"pi_{sample['prompt_id']:03d}",
                    "base_prompt": sample['test_case_prompt'],
                    "injection_prompt": sample['user_input'],
                    "expected_behavior": "refuse_to_reveal",
                    "judge_question": sample['judge_question'],
                    "success_criteria": "no_secret_revealed",
                    "severity": "critical",
                    "language": sample['speaking_language'],
                    "technique": sample['injection_variant'],
                    "risk_category": sample['risk_category']
                })
            
            return transformed_samples
            
        except Exception as e:
            print(f"❌ Error loading dataset: {e}")
            return []
    
    async def test_validation_agent(self) -> bool:
        """Test the validation agent."""
        print("\n🔐 Testing Validation Agent...")
        
        try:
            config = {
                'test': True,
                'openai_api_key': self.api_key
            }
            
            agent = PromptInjectionValidationAgent(config, 'validation_test')
            
            # Test validation data
            validation_data = {
                "api_key": self.api_key,
                "model": self.target_model,
                "user_id": "integration_test_user",
                "dataset_path": "prompt_injection.json"
            }
            
            print("   Validating API key and model...")
            result = await agent.execute(validation_data)
            
            if result.success:
                print(f"✅ Validation successful")
                print(f"   Confidence: {result.confidence}")
                return True
            else:
                print(f"❌ Validation failed: {result.error}")
                return False
                
        except Exception as e:
            print(f"❌ Validation agent error: {e}")
            return False
    
    async def test_execution_agent(self, test_samples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Test the execution agent with real API calls."""
        print("\n⚡ Testing Execution Agent...")
        
        try:
            config = {
                'test': True,
                'openai_api_key': self.api_key
            }
            
            agent = PromptInjectionTestExecutionAgent(config, 'execution_test')
            
            # Prepare execution data
            execution_data = {
                "session_id": f"integration_test_{int(time.time())}",
                "api_key": self.api_key,
                "model": self.target_model,
                "user_id": "integration_test_user",
                "dataset_path": "prompt_injection.json",
                "batch_size": 5,  # Process in small batches
                "max_tokens": 150,
                "temperature": 0.7
            }
            
            print(f"   Executing tests on {len(test_samples)} samples...")
            print(f"   Target model: {self.target_model}")
            
            result = await agent.execute(execution_data)
            
            if result.success:
                print(f"✅ Execution successful")
                print(f"   Confidence: {result.confidence}")
                
                # Extract test results
                test_results = result.data.get('results', [])
                print(f"   Generated {len(test_results)} test results")
                
                return test_results
            else:
                print(f"❌ Execution failed: {result.error}")
                return []
                
        except Exception as e:
            print(f"❌ Execution agent error: {e}")
            return []
    
    async def test_evaluation_agent(self, test_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Test the evaluation agent with LLM-as-a-Judge."""
        print("\n🧠 Testing Evaluation Agent (LLM-as-a-Judge)...")
        
        try:
            config = {
                'test': True,
                'openai_api_key': self.api_key,
                'judge_model': self.judge_model
            }
            
            agent = PromptInjectionEvaluationAgent(config, 'evaluation_test')
            
            # Prepare evaluation data
            evaluation_data = {
                "session_id": f"integration_test_{int(time.time())}",
                "api_key": self.api_key,
                "judge_model": self.judge_model,
                "test_results": test_results
            }
            
            print(f"   Evaluating {len(test_results)} responses...")
            print(f"   Judge model: {self.judge_model}")
            
            result = await agent.execute(evaluation_data)
            
            if result.success:
                print(f"✅ Evaluation successful")
                print(f"   Confidence: {result.confidence}")
                
                # Extract evaluated results
                evaluated_results = result.data.get('evaluated_results', [])
                successful_resistances = result.data.get('successful_resistances', 0)
                failed_resistances = result.data.get('failed_resistances', 0)
                
                print(f"   Successful resistances: {successful_resistances}")
                print(f"   Failed resistances: {failed_resistances}")
                print(f"   Detection rate: {(successful_resistances / len(evaluated_results) * 100):.1f}%")
                
                return evaluated_results
            else:
                print(f"❌ Evaluation failed: {result.error}")
                return []
                
        except Exception as e:
            print(f"❌ Evaluation agent error: {e}")
            return []
    
    async def test_report_analysis_agent(self, evaluated_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test the report analysis agent."""
        print("\n📊 Testing Report Analysis Agent...")
        
        try:
            config = {'test': True}
            agent = PromptInjectionReportAnalysisAgent(config, 'report_test')
            
            # Prepare report data
            report_data = {
                "session_id": f"integration_test_{int(time.time())}",
                "evaluated_results": evaluated_results,
                "successful_resistances": sum(1 for r in evaluated_results if r.get('success', False)),
                "failed_resistances": sum(1 for r in evaluated_results if not r.get('success', False))
            }
            
            print(f"   Analyzing {len(evaluated_results)} evaluated results...")
            
            result = await agent.execute(report_data)
            
            if result.success:
                print(f"✅ Report analysis successful")
                print(f"   Confidence: {result.confidence}")
                
                # Extract report data
                final_report = result.data.get('final_report', {})
                ui_data = result.data.get('ui_data', {})
                
                print(f"   Generated comprehensive report")
                print(f"   UI data formatted for frontend")
                
                return {
                    'final_report': final_report,
                    'ui_data': ui_data
                }
            else:
                print(f"❌ Report analysis failed: {result.error}")
                return {}
                
        except Exception as e:
            print(f"❌ Report analysis agent error: {e}")
            return {}
    
    async def run_complete_integration_test(self):
        """Run the complete multi-agent integration test."""
        print("🚀 Starting Multi-Agent Integration Test")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # Step 1: Load test dataset
        test_samples = await self.load_test_dataset(25)
        if not test_samples:
            print("❌ Failed to load test dataset")
            return False
        
        # Step 2: Test validation agent
        validation_success = await self.test_validation_agent()
        if not validation_success:
            print("❌ Validation failed, stopping test")
            return False
        
        # Step 3: Test execution agent
        test_results = await self.test_execution_agent(test_samples)
        if not test_results:
            print("❌ Execution failed, stopping test")
            return False
        
        # Step 4: Test evaluation agent
        evaluated_results = await self.test_evaluation_agent(test_results)
        if not evaluated_results:
            print("❌ Evaluation failed, stopping test")
            return False
        
        # Step 5: Test report analysis agent
        report_data = await self.test_report_analysis_agent(evaluated_results)
        if not report_data:
            print("❌ Report analysis failed")
            return False
        
        self.end_time = time.time()
        
        # Generate final report
        await self.generate_final_report(report_data)
        
        return True
    
    async def generate_final_report(self, report_data: Dict[str, Any]):
        """Generate the final integration test report."""
        print("\n" + "=" * 60)
        print("📋 INTEGRATION TEST COMPLETE")
        print("=" * 60)
        
        duration = self.end_time - self.start_time
        print(f"⏱️  Total execution time: {duration:.2f} seconds")
        
        if 'ui_data' in report_data:
            ui_data = report_data['ui_data']
            
            print(f"\n📊 DASHBOARD SUMMARY:")
            if 'dashboard_summary' in ui_data:
                summary = ui_data['dashboard_summary']
                print(f"   Total tests: {summary.get('total_tests', 0)}")
                print(f"   Successful resistances: {summary.get('successful_resistances', 0)}")
                print(f"   Failed resistances: {summary.get('failed_resistances', 0)}")
                print(f"   Detection rate: {summary.get('detection_rate', 0):.1f}%")
                print(f"   Average response time: {summary.get('average_response_time', 0):.3f}s")
            
            print(f"\n📈 CHARTS DATA:")
            if 'charts_data' in ui_data:
                charts = ui_data['charts_data']
                print(f"   Severity distribution: {len(charts.get('severity_distribution', []))} categories")
                print(f"   Technique distribution: {len(charts.get('technique_distribution', []))} categories")
                print(f"   Risk distribution: {len(charts.get('risk_distribution', []))} categories")
            
            print(f"\n💡 RECOMMENDATIONS:")
            if 'recommendations' in ui_data:
                recommendations = ui_data['recommendations']
                for i, rec in enumerate(recommendations[:5], 1):  # Show first 5
                    print(f"   {i}. {rec}")
        
        print(f"\n🎉 INTEGRATION TEST SUCCESSFUL!")
        print(f"✅ All agents working correctly")
        print(f"✅ Real API calls completed")
        print(f"✅ LLM-as-a-Judge evaluation working")
        print(f"✅ UI data generated for frontend")
        print(f"✅ Multi-agent system fully functional")

async def main():
    """Main function to run the integration test."""
    test = MultiAgentIntegrationTest()
    success = await test.run_complete_integration_test()
    
    if success:
        print("\n🚀 Multi-Agent System is ready for production!")
    else:
        print("\n❌ Integration test failed - check logs above")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
