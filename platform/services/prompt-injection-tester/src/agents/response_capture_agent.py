"""
Response Capture Agent - Captures all responses from GPT-3.5-turbo and stores them temporarily.
"""

import sys
import os
import json
import time
import asyncio
from typing import Dict, Any, List
from openai import AsyncOpenAI

sys.path.append(os.path.join(os.path.dirname(__file__), "../../../libs"))
from base_agent import AgentResult, BaseAgent

class ResponseCaptureAgent(BaseAgent):
    """Agent that captures responses from GPT-3.5-turbo and stores them temporarily."""
    
    def __init__(self, config: Dict[str, Any], agent_id: str = "response_capture_agent"):
        super().__init__(config, agent_id)
        self.module_type = "prompt_injection"
        self.captured_responses = []
        
    async def execute(self, state: Dict[str, Any]) -> AgentResult:
        """
        Capture responses from GPT-3.5-turbo for all samples in prompt_injection.json.
        
        Args:
            state: Workflow state containing capture parameters
            
        Returns:
            AgentResult: Capture result with stored responses
        """
        try:
            await self.pre_execute(state)
            
            # Extract parameters
            api_key = state.get("api_key")
            model = state.get("model", "gpt-3.5-turbo")
            dataset_path = state.get("dataset_path", "prompt_injection.json")
            max_tokens = state.get("max_tokens", 150)
            temperature = state.get("temperature", 0.7)
            user_id = state.get("user_id")
            
            if not api_key:
                return AgentResult(
                    success=False,
                    data={},
                    error="API key is required for response capture",
                    confidence=0.0
                )
            
            # Load dataset
            dataset = await self._load_dataset(dataset_path)
            if not dataset:
                return AgentResult(
                    success=False,
                    data={},
                    error="Failed to load dataset",
                    confidence=0.0
                )
            
            print(f"📊 Capturing responses for {len(dataset)} samples from {dataset_path}")
            print(f"🤖 Target model: {model}")
            
            # Initialize OpenAI client using modern method
            client = AsyncOpenAI(api_key=api_key)
            
            # Capture responses for each sample
            captured_responses = []
            successful_captures = 0
            failed_captures = 0
            
            for i, sample in enumerate(dataset):
                try:
                    print(f"   Processing sample {i+1}/{len(dataset)}: {sample.get('prompt_id', 'unknown')}")
                    
                    # Make API call to GPT-3.5-turbo using modern method
                    start_time = time.time()
                    response = await client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "user", "content": sample["user_input"]}
                        ],
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                    response_time = time.time() - start_time
                    
                    # Extract response
                    model_response = response.choices[0].message.content
                    
                    # Store captured response
                    captured_response = {
                        "sample_id": f"pi_{sample['prompt_id']:03d}",
                        "prompt_id": sample["prompt_id"],
                        "test_case_prompt": sample["test_case_prompt"],
                        "user_input": sample["user_input"],
                        "judge_question": sample["judge_question"],
                        "injection_variant": sample["injection_variant"],
                        "injection_type": sample["injection_type"],
                        "risk_category": sample["risk_category"],
                        "speaking_language": sample["speaking_language"],
                        "model_response": model_response,
                        "response_time": response_time,
                        "api_model": model,
                        "api_temperature": temperature,
                        "api_max_tokens": max_tokens,
                        "capture_timestamp": time.time(),
                        "capture_success": True
                    }
                    
                    captured_responses.append(captured_response)
                    successful_captures += 1
                    
                    print(f"     ✅ Response captured ({response_time:.3f}s)")
                    
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    print(f"     ❌ Failed to capture response: {str(e)}")
                    
                    # Store failed capture
                    failed_response = {
                        "sample_id": f"pi_{sample['prompt_id']:03d}",
                        "prompt_id": sample["prompt_id"],
                        "test_case_prompt": sample["test_case_prompt"],
                        "user_input": sample["user_input"],
                        "judge_question": sample["judge_question"],
                        "injection_variant": sample["injection_variant"],
                        "injection_type": sample["injection_type"],
                        "risk_category": sample["risk_category"],
                        "speaking_language": sample["speaking_language"],
                        "model_response": f"API Error: {str(e)}",
                        "response_time": 0.0,
                        "api_model": model,
                        "api_temperature": temperature,
                        "api_max_tokens": max_tokens,
                        "capture_timestamp": time.time(),
                        "capture_success": False,
                        "error": str(e)
                    }
                    
                    captured_responses.append(failed_response)
                    failed_captures += 1
                    
                    # Continue with next sample
                    continue
            
            # Store captured responses to temporary file
            temp_file_path = f"temp_captured_responses_{int(time.time())}.json"
            await self._store_responses(captured_responses, temp_file_path)
            
            print(f"\n📁 Captured responses stored in: {temp_file_path}")
            print(f"✅ Successful captures: {successful_captures}")
            print(f"❌ Failed captures: {failed_captures}")
            
            # Prepare result data
            result_data = {
                "captured_responses": captured_responses,
                "temp_file_path": temp_file_path,
                "total_samples": len(dataset),
                "successful_captures": successful_captures,
                "failed_captures": failed_captures,
                "capture_rate": (successful_captures / len(dataset)) * 100,
                "api_model": model,
                "dataset_path": dataset_path
            }
            
            return AgentResult(
                success=True,
                data=result_data,
                confidence=1.0,
                metadata={"capture_type": "gpt_3_5_turbo_responses"}
            )
            
        except Exception as e:
            return await self.handle_error(e)
    
    async def _load_dataset(self, dataset_path: str) -> List[Dict[str, Any]]:
        """Load the prompt injection dataset."""
        try:
            with open(f'data/{dataset_path}', 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            return dataset
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return []
    
    async def _store_responses(self, responses: List[Dict[str, Any]], file_path: str):
        """Store captured responses to temporary file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(responses, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error storing responses: {e}")
    
    async def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data for response capture."""
        required_fields = ["api_key", "model", "user_id"]
        return all(field in data for field in required_fields)
