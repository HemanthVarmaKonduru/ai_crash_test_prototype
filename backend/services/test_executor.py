"""
Test execution service for running security tests.
"""
import sys
import os
import json
import time
import re
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
from openai import AsyncOpenAI

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.config.settings import (
    API_KEY, TARGET_MODEL, JUDGE_MODEL,
    MAX_PROMPTS_PI, MAX_PROMPTS_JB, MAX_PROMPTS_DE, MAX_PROMPTS_ADVERSARIAL,
    PROMPT_INJECTION_DATASET, JAILBREAK_DATASET, DATA_EXTRACTION_DATASET, ADVERSARIAL_ATTACKS_DATASET,
    USE_OLLAMA_FOR_EVALUATION, OLLAMA_API_KEY, OLLAMA_HOST, OLLAMA_JUDGE_MODEL
)
from backend.utils.llm_client import LLMClient
from backend.services.prompt_injection.evaluation import (
    PromptInjectionEvaluator,
    EvaluationContext,
    create_evaluator_with_defaults
)
from backend.services.jailbreak.evaluation import (
    JailbreakEvaluator,
    EvaluationContext as JailbreakEvaluationContext,
    create_evaluator_with_defaults as create_jailbreak_evaluator_with_defaults
)
from backend.services.data_extraction.evaluation import (
    DataExtractionEvaluator,
    EvaluationContext as DataExtractionEvaluationContext,
    create_evaluator_with_defaults as create_data_extraction_evaluator_with_defaults
)
from backend.services.adversarial_attacks.evaluation import (
    AdversarialAttacksEvaluator,
    EvaluationContext as AdversarialAttacksEvaluationContext,
    create_evaluator_with_defaults as create_adversarial_attacks_evaluator_with_defaults
)
from backend.services.analytics import AnalyticsService
from backend.services.analytics.token_counter import extract_token_usage

def get_evaluation_client():
    """Get the appropriate LLM client for evaluation based on configuration."""
    if USE_OLLAMA_FOR_EVALUATION:
        return LLMClient(
            provider="ollama",
            api_key=OLLAMA_API_KEY,
            host=OLLAMA_HOST
        ), OLLAMA_JUDGE_MODEL
    else:
        return LLMClient(
            provider="openai",
            api_key=API_KEY
        ), JUDGE_MODEL

async def execute_prompt_injection_test(test_id: str, session: Dict[str, Any]) -> None:
    """Execute prompt injection test."""
    try:
        print(f"🚀 Starting prompt injection test: {test_id}")
        # Load dataset
        session["status"] = "running"
        session["current_step"] = "Loading prompt injection dataset..."
        session["progress"] = 5
        print(f"📊 Progress: {session['progress']}% - {session['current_step']}")
        
        if not PROMPT_INJECTION_DATASET.exists():
            raise Exception("Prompt injection dataset not found")
        
        with open(PROMPT_INJECTION_DATASET, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        all_samples = dataset.get('prompt_injection_samples', [])
        limited_samples = all_samples[:MAX_PROMPTS_PI]
        
        session["total_tests"] = len(limited_samples)
        session["current_step"] = f"Testing {len(limited_samples)} prompts..."
        session["progress"] = 10
        
        # Capture responses
        client = AsyncOpenAI(api_key=API_KEY)
        captured_responses = []
        
        for i, sample in enumerate(limited_samples):
            progress = 15 + (i / len(limited_samples)) * 40
            session["progress"] = int(progress)
            session["completed_tests"] = i
            session["current_step"] = f"Processing sample {i+1}/{len(limited_samples)}: {sample.get('sample_id', 'N/A')}"
            
            try:
                response_start = time.time()
                response = await client.chat.completions.create(
                    model=TARGET_MODEL,
                    messages=[
                        {"role": "system", "content": sample.get('base_prompt', 'You are a helpful AI assistant.')},
                        {"role": "user", "content": sample.get('injection_prompt', '')}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                response_time = time.time() - response_start
                
                # Extract token usage
                token_usage = extract_token_usage(response)
                
                captured_responses.append({
                    "sample_id": sample.get('sample_id', f'pi_{i+1:03d}'),
                    "category": sample.get('category', 'unknown'),
                    "technique": sample.get('technique', 'unknown'),
                    "severity": sample.get('severity', 'unknown'),
                    "language": sample.get('language', 'English'),
                    "base_prompt": sample.get('base_prompt', ''),
                    "injection_prompt": sample.get('injection_prompt', ''),
                    "model_response": response.choices[0].message.content,
                    "response_time": response_time,
                    "api_model": TARGET_MODEL,
                    "capture_success": True,
                    "token_usage": token_usage,
                    "usage": token_usage  # Also store as 'usage' for compatibility
                })
            except Exception as e:
                print(f"Failed to capture response for sample {i+1}: {e}")
                continue
        
        session["captured_responses"] = captured_responses
        
        # Initialize new multi-layer evaluator
        print(f"🔧 Initializing evaluator for test: {test_id}")
        try:
            evaluator = create_evaluator_with_defaults()
            print(f"✅ Evaluator created, initializing...")
            await evaluator.initialize()
            print(f"✅ Evaluator initialized successfully")
        except Exception as e:
            import traceback
            print(f"❌ Failed to initialize evaluator: {e}")
            print(f"📋 Traceback:\n{traceback.format_exc()}")
            raise
        
        eval_provider = "Multi-Layer Evaluation (Layer 1 + Layer 3)"
        session["current_step"] = f"Evaluating responses with {eval_provider}..."
        session["progress"] = 60
        print(f"📊 Progress: {session['progress']}% - {session['current_step']}")
        
        # Evaluate responses using new evaluator
        evaluated_responses = []
        successful_resistances = 0
        failed_resistances = 0
        
        for i, captured in enumerate(captured_responses):
            progress = 60 + (i / len(captured_responses)) * 35
            session["progress"] = int(progress)
            session["current_step"] = f"Evaluating response {i+1}/{len(captured_responses)}"
            
            try:
                # Create evaluation context
                context = EvaluationContext(
                    injection_prompt=captured.get('injection_prompt', ''),
                    model_response=captured.get('model_response', ''),
                    base_prompt=captured.get('base_prompt', ''),
                    sample_metadata={
                        'sample_id': captured.get('sample_id', ''),
                        'category': captured.get('category', 'unknown'),
                        'technique': captured.get('technique', 'unknown'),
                        'severity': captured.get('severity', 'unknown'),
                        'language': captured.get('language', 'English')
                    },
                    response_time=captured.get('response_time', 0.0)
                )
                
                # Track evaluation time
                evaluation_start = time.time()
                
                # Evaluate using new multi-layer system
                evaluation_result = await evaluator.evaluate(context)
                
                evaluation_time = time.time() - evaluation_start
                
                # Convert to format compatible with existing code
                evaluated_responses.append({
                    **captured,
                    "injection_successful": evaluation_result.injection_successful,
                    "confidence_score": evaluation_result.confidence_score,
                    "safety_score": evaluation_result.safety_score,
                    "severity": evaluation_result.severity.value,
                    "reasoning": evaluation_result.reasoning,
                    "response_time": captured.get('response_time', 0.0),  # API call time
                    "evaluation_time": evaluation_time,  # Evaluation processing time
                    "evaluation": {
                        "injection_successful": evaluation_result.injection_successful,
                        "confidence_score": evaluation_result.confidence_score,
                        "severity": evaluation_result.severity.value,
                        "safety_score": evaluation_result.safety_score,
                        "reasoning": evaluation_result.reasoning,
                        "evaluation_layer": evaluation_result.evaluation_layer.value,
                        "outcome": evaluation_result.outcome.value,
                        "detected_patterns": evaluation_result.detected_patterns,
                        "signal_breakdown": evaluation_result.signal_breakdown
                    },
                    "evaluation_metadata": {
                        "layer_used": evaluation_result.evaluation_layer.value,
                        "false_positive_checked": evaluation_result.false_positive_checked
                    }
                })
                
                if not evaluation_result.injection_successful:
                    successful_resistances += 1
                else:
                    failed_resistances += 1
                    
            except Exception as e:
                print(f"Failed to evaluate response {i+1}: {e}")
                # Fallback to basic evaluation if new evaluator fails
                evaluated_responses.append({
                    **captured,
                    "injection_successful": False,
                    "confidence_score": 0.5,
                    "safety_score": 0.5,
                    "reasoning": f"Evaluation error: {str(e)}",
                    "evaluation": {"error": str(e)}
                })
                successful_resistances += 1  # Conservative: assume resistance if evaluation fails
                continue
        
        # Finalize results
        session["progress"] = 95
        detection_rate = (successful_resistances / len(evaluated_responses)) * 100 if evaluated_responses else 0
        
        technique_stats = {}
        severity_stats = {}
        language_stats = {}
        
        for result in evaluated_responses:
            technique_stats[result.get('technique', 'unknown')] = technique_stats.get(result.get('technique', 'unknown'), 0) + 1
            severity_stats[result.get('severity', 'unknown')] = severity_stats.get(result.get('severity', 'unknown'), 0) + 1
            language_stats[result.get('language', 'unknown')] = language_stats.get(result.get('language', 'unknown'), 0) + 1
        
        # Calculate total execution time correctly
        end_time = datetime.now()
        start_time_dt = datetime.fromisoformat(session["start_time"])
        total_execution_time = (end_time - start_time_dt).total_seconds()
        
        session["evaluated_responses"] = evaluated_responses
        session["results"] = {
            "detection_rate": detection_rate,
            "successful_resistances": successful_resistances,
            "failed_resistances": failed_resistances,
            "successful_captures": len(captured_responses),
            "failed_captures": 0,
            "successful_evaluations": len(evaluated_responses),
            "total_execution_time": total_execution_time,
            "detailed_analysis": {
                "technique_distribution": technique_stats,
                "severity_distribution": severity_stats,
                "language_distribution": language_stats
            },
            "performance_metrics": {
                "average_response_time": sum(r.get('response_time', 0) for r in captured_responses) / len(captured_responses) if captured_responses else 0,
                "total_api_calls": len(captured_responses) + len(evaluated_responses),
                "total_execution_time": total_execution_time
            }
        }
        
        session["status"] = "completed"
        session["progress"] = 100
        session["completed_tests"] = len(evaluated_responses)
        session["current_step"] = "Test completed successfully!"
        session["end_time"] = end_time.isoformat()
        
        # Record analytics
        try:
            eval_client, judge_model = get_evaluation_client()
            analytics_service = AnalyticsService()
            await analytics_service.record_test_run(
                test_id=test_id,
                test_type="prompt_injection",
                session=session,
                captured_responses=captured_responses,
                evaluated_responses=evaluated_responses,
                target_model=TARGET_MODEL,
                judge_model=judge_model,
            )
            print(f"✅ Analytics recorded for test {test_id}")
        except Exception as analytics_error:
            print(f"⚠️ Warning: Could not record analytics: {analytics_error}")
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        session["status"] = "failed"
        session["error"] = str(e)
        session["current_step"] = f"Test failed: {str(e)}"
        print(f"❌ Test {test_id} failed: {e}")
        print(f"📋 Full traceback:\n{error_traceback}")

async def execute_jailbreak_test(test_id: str, session: Dict[str, Any]) -> None:
    """Execute jailbreak test with multi-layer evaluation."""
    try:
        print(f"🚀 Starting jailbreak test: {test_id}")
        session["status"] = "running"
        session["current_step"] = "Loading jailbreak dataset..."
        session["progress"] = 5
        
        if not JAILBREAK_DATASET.exists():
            raise Exception("Jailbreak dataset not found")
        
        with open(JAILBREAK_DATASET, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        # Jailbreak dataset is a direct array, not nested in 'jailbreak_samples'
        all_samples = dataset if isinstance(dataset, list) else dataset.get('jailbreak_samples', [])
        limited_samples = all_samples[:MAX_PROMPTS_JB]
        
        session["total_tests"] = len(limited_samples)
        session["current_step"] = f"Testing {len(limited_samples)} jailbreak prompts..."
        session["progress"] = 10
        print(f"📊 Progress: {session['progress']}% - {session['current_step']}")
        
        # Capture responses
        client = AsyncOpenAI(api_key=API_KEY)
        captured_responses = []
        
        for i, sample in enumerate(limited_samples):
            progress = 15 + (i / len(limited_samples)) * 40
            session["progress"] = int(progress)
            session["completed_tests"] = i
            session["current_step"] = f"Capturing response {i+1}/{len(limited_samples)}..."
            
            try:
                response_start = time.time()
                # Map jailbreak.json fields to API call
                test_case_prompt = sample.get('test_case_prompt', 'You are a helpful AI assistant. Follow safety guidelines and provide helpful, harmless responses.')
                user_input = sample.get('user_input', '')
                
                response = await client.chat.completions.create(
                    model=TARGET_MODEL,
                    messages=[
                        {"role": "system", "content": test_case_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                response_time = time.time() - response_start
                
                # Extract token usage
                token_usage = extract_token_usage(response)
                
                captured_responses.append({
                    "sample_id": sample.get('prompt_id', f'jb_{i+1:03d}'),
                    "injection_variant": sample.get('injection_variant', 'unknown'),
                    "technique": sample.get('technique', 'unknown'),
                    "risk_category": sample.get('risk_category', 'unknown'),
                    "test_case_prompt": test_case_prompt,
                    "jailbreak_prompt": user_input,
                    "judge_question": sample.get('judge_question', ''),
                    "model_response": response.choices[0].message.content,
                    "response_time": response_time,
                    "api_model": TARGET_MODEL,
                    "language": sample.get('speaking_language', 'English'),
                    "capture_success": True,
                    "token_usage": token_usage,
                    "usage": token_usage  # Also store as 'usage' for compatibility
                })
            except Exception as e:
                print(f"❌ Failed to capture response {i+1}: {e}")
                import traceback
                print(f"📋 Traceback:\n{traceback.format_exc()}")
                continue
        
        session["captured_responses"] = captured_responses
        print(f"✅ Captured {len(captured_responses)} responses")
        
        # Initialize new multi-layer evaluator
        print(f"🔧 Initializing jailbreak evaluator for test: {test_id}")
        try:
            evaluator = create_jailbreak_evaluator_with_defaults()
            print(f"✅ Evaluator created, initializing...")
            await evaluator.initialize()
            print(f"✅ Evaluator initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize evaluator: {e}")
            import traceback
            print(f"📋 Traceback:\n{traceback.format_exc()}")
            raise
        
        eval_provider = "Multi-Layer Evaluation (Layer 1 + Layer 3)"
        session["current_step"] = f"Evaluating responses with {eval_provider}..."
        session["progress"] = 60
        print(f"📊 Progress: {session['progress']}% - {session['current_step']}")
        
        # Evaluate responses using new multi-layer system
        evaluated_responses = []
        successful_resistances = 0
        failed_resistances = 0
        
        for i, captured in enumerate(captured_responses):
            progress = 60 + (i / len(captured_responses)) * 35
            session["progress"] = int(progress)
            session["current_step"] = f"Evaluating response {i+1}/{len(captured_responses)}"
            
            try:
                # Create evaluation context
                context = JailbreakEvaluationContext(
                    jailbreak_prompt=captured.get('jailbreak_prompt', ''),
                    model_response=captured.get('model_response', ''),
                    test_case_prompt=captured.get('test_case_prompt', ''),
                    judge_question=captured.get('judge_question'),
                    sample_metadata={
                        'sample_id': captured.get('sample_id', ''),
                        'injection_variant': captured.get('injection_variant', 'unknown'),
                        'technique': captured.get('technique', 'unknown'),
                        'risk_category': captured.get('risk_category', 'unknown'),
                        'language': captured.get('language', 'English')
                    },
                    response_time=captured.get('response_time', 0.0)
                )
                
                # Track evaluation time
                evaluation_start = time.time()
                
                # Evaluate using new multi-layer system
                evaluation_result = await evaluator.evaluate(context)
                
                evaluation_time = time.time() - evaluation_start
                
                # Convert to format compatible with existing code
                evaluated_responses.append({
                    **captured,
                    "jailbreak_successful": evaluation_result.jailbreak_successful,
                    "confidence_score": evaluation_result.confidence_score,
                    "safety_score": evaluation_result.safety_score,
                    "severity": evaluation_result.severity.value,
                    "reasoning": evaluation_result.reasoning,
                    "response_time": captured.get('response_time', 0.0),  # API call time
                    "evaluation_time": evaluation_time,  # Evaluation processing time
                    "evaluation": {
                        "jailbreak_successful": evaluation_result.jailbreak_successful,
                        "confidence_score": evaluation_result.confidence_score,
                        "severity": evaluation_result.severity.value,
                        "safety_score": evaluation_result.safety_score,
                        "reasoning": evaluation_result.reasoning,
                        "evaluation_layer": evaluation_result.evaluation_layer.value,
                        "outcome": evaluation_result.outcome.value,
                        "detected_patterns": evaluation_result.detected_patterns,
                        "signal_breakdown": evaluation_result.signal_breakdown
                    },
                    "evaluation_metadata": {
                        "layer_used": evaluation_result.evaluation_layer.value,
                        "false_positive_checked": evaluation_result.false_positive_checked
                    }
                })
                
                if not evaluation_result.jailbreak_successful:
                    successful_resistances += 1
                else:
                    failed_resistances += 1
                    
            except Exception as e:
                print(f"❌ Failed to evaluate response {i+1}: {e}")
                import traceback
                print(f"📋 Traceback:\n{traceback.format_exc()}")
                # Fallback to basic evaluation if new evaluator fails
                evaluated_responses.append({
                    **captured,
                    "jailbreak_successful": False,
                    "confidence_score": 0.5,
                    "safety_score": 0.5,
                    "reasoning": f"Evaluation error: {str(e)}",
                    "evaluation": {"error": str(e)}
                })
                successful_resistances += 1  # Conservative: assume resistance if evaluation fails
                continue
        
        # Finalize results
        session["progress"] = 95
        detection_rate = (successful_resistances / len(evaluated_responses)) * 100 if evaluated_responses else 0
        
        print(f"✅ Evaluation completed: {successful_resistances} resistances, {failed_resistances} vulnerabilities")
        
        # Calculate total execution time correctly
        end_time = datetime.now()
        start_time_dt = datetime.fromisoformat(session["start_time"])
        total_execution_time = (end_time - start_time_dt).total_seconds()
        
        session["evaluated_responses"] = evaluated_responses
        session["results"] = {
            "detection_rate": detection_rate,
            "successful_resistances": successful_resistances,
            "failed_resistances": failed_resistances,
            "successful_captures": len(captured_responses),
            "successful_evaluations": len(evaluated_responses),
            "total_execution_time": total_execution_time,
            "performance_metrics": {
                "average_response_time": sum(r.get('response_time', 0) for r in captured_responses) / len(captured_responses) if captured_responses else 0,
                "total_api_calls": len(captured_responses),
                "total_execution_time": total_execution_time
            }
        }
        
        session["status"] = "completed"
        session["progress"] = 100
        session["completed_tests"] = len(evaluated_responses)
        session["current_step"] = "Test completed successfully!"
        session["end_time"] = end_time.isoformat()
        
        # Record analytics
        try:
            eval_client, judge_model = get_evaluation_client()
            analytics_service = AnalyticsService()
            await analytics_service.record_test_run(
                test_id=test_id,
                test_type="jailbreak",
                session=session,
                captured_responses=captured_responses,
                evaluated_responses=evaluated_responses,
                target_model=TARGET_MODEL,
                judge_model=judge_model,
            )
            print(f"✅ Analytics recorded for test {test_id}")
        except Exception as analytics_error:
            print(f"⚠️ Warning: Could not record analytics: {analytics_error}")
        
        print(f"✅ Jailbreak test {test_id} completed successfully")
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        session["status"] = "failed"
        session["error"] = str(e)
        session["current_step"] = f"Test failed: {str(e)}"
        print(f"❌ Jailbreak test {test_id} failed: {e}")
        print(f"📋 Full traceback:\n{error_traceback}")

async def execute_data_extraction_test(test_id: str, session: Dict[str, Any]) -> None:
    """Execute data extraction test."""
    try:
        session["status"] = "running"
        session["current_step"] = "Loading data extraction dataset..."
        session["progress"] = 5
        
        if not DATA_EXTRACTION_DATASET.exists():
            raise Exception("Data extraction dataset not found")
        
        with open(DATA_EXTRACTION_DATASET, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        all_samples = dataset.get('data_extraction_samples', [])
        limited_samples = all_samples[:MAX_PROMPTS_DE]
        
        session["total_tests"] = len(limited_samples)
        session["current_step"] = f"Testing {len(limited_samples)} data extraction prompts..."
        session["progress"] = 10
        print(f"📊 Progress: {session['progress']}% - {session['current_step']}")
        
        # Capture responses
        client = AsyncOpenAI(api_key=API_KEY)
        captured_responses = []
        
        for i, sample in enumerate(limited_samples):
            progress = 15 + (i / len(limited_samples)) * 40
            session["progress"] = int(progress)
            session["completed_tests"] = i
            
            try:
                response_start = time.time()
                response = await client.chat.completions.create(
                    model=TARGET_MODEL,
                    messages=[
                        {"role": "system", "content": sample.get('base_prompt', 'You are a helpful AI assistant.')},
                        {"role": "user", "content": sample.get('extraction_prompt', '')}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                response_time = time.time() - response_start
                
                # Extract token usage
                token_usage = extract_token_usage(response)
                
                captured_responses.append({
                    "sample_id": sample.get('sample_id', f'de_{i+1:03d}'),
                    "category": sample.get('category', 'unknown'),
                    "technique": sample.get('technique', 'unknown'),
                    "severity": sample.get('severity', 'unknown'),
                    "risk_category": sample.get('risk_category', 'unknown'),
                    "language": sample.get('language', 'English'),
                    "base_prompt": sample.get('base_prompt', ''),
                    "extraction_prompt": sample.get('extraction_prompt', ''),
                    "model_response": response.choices[0].message.content,
                    "response_time": response_time,
                    "api_model": TARGET_MODEL,
                    "capture_success": True,
                    "token_usage": token_usage,
                    "usage": token_usage  # Also store as 'usage' for compatibility
                })
            except Exception as e:
                print(f"❌ Failed to capture response {i+1}: {e}")
                import traceback
                print(f"📋 Traceback:\n{traceback.format_exc()}")
                continue
        
        session["captured_responses"] = captured_responses
        print(f"✅ Captured {len(captured_responses)} responses")

        # Initialize new multi-layer evaluator
        print(f"🔧 Initializing data extraction evaluator for test: {test_id}")
        try:
            evaluator = create_data_extraction_evaluator_with_defaults()
            print(f"✅ Evaluator created, initializing...")
            await evaluator.initialize()
            print(f"✅ Evaluator initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize evaluator: {e}")
            import traceback
            print(f"📋 Traceback:\n{traceback.format_exc()}")
            raise

        eval_provider = "Multi-Layer Evaluation (Layer 1 + Layer 3)"
        session["current_step"] = f"Evaluating responses with {eval_provider}..."
        session["progress"] = 60
        print(f"📊 Progress: {session['progress']}% - {session['current_step']}")

        # Evaluate responses using new multi-layer system
        evaluated_responses = []
        successful_resistances = 0
        failed_extractions = 0

        for i, captured in enumerate(captured_responses):
            progress = 60 + (i / len(captured_responses)) * 35
            session["progress"] = int(progress)
            session["current_step"] = f"Evaluating response {i+1}/{len(captured_responses)}"

            try:
                # Create evaluation context
                context = DataExtractionEvaluationContext(
                    base_prompt=captured.get('base_prompt', ''),
                    extraction_prompt=captured.get('extraction_prompt', ''),
                    model_response=captured.get('model_response', ''),
                    judge_question=None,  # Will use default from evaluator
                    sample_metadata={
                        'sample_id': captured.get('sample_id', ''),
                        'category': captured.get('category', 'unknown'),
                        'technique': captured.get('technique', 'unknown'),
                        'severity': captured.get('severity', 'medium'),
                        'risk_category': captured.get('risk_category', 'unknown'),
                        'language': captured.get('language', 'English')
                    },
                    response_time=captured.get('response_time', 0.0)
                )

                # Track evaluation time
                evaluation_start = time.time()

                # Evaluate using new multi-layer system
                evaluation_result = await evaluator.evaluate(context)

                evaluation_time = time.time() - evaluation_start

                # Convert to format compatible with existing code
                evaluated_responses.append({
                    **captured,
                    "data_extraction_successful": evaluation_result.data_extraction_successful,
                    "extraction_successful": evaluation_result.data_extraction_successful,  # Alias for compatibility
                    "confidence_score": evaluation_result.confidence_score,
                    "safety_score": evaluation_result.safety_score,
                    "privacy_score": evaluation_result.privacy_score,
                    "severity": evaluation_result.severity.value,
                    "reasoning": evaluation_result.reasoning,
                    "response_time": captured.get('response_time', 0.0),  # API call time
                    "evaluation_time": evaluation_time,  # Evaluation processing time
                    "evaluation": {
                        "data_extraction_successful": evaluation_result.data_extraction_successful,
                        "confidence_score": evaluation_result.confidence_score,
                        "severity": evaluation_result.severity.value,
                        "safety_score": evaluation_result.safety_score,
                        "privacy_score": evaluation_result.privacy_score,
                        "reasoning": evaluation_result.reasoning,
                        "evaluation_layer": evaluation_result.evaluation_layer.value,
                        "outcome": evaluation_result.outcome.value,
                        "detected_patterns": evaluation_result.detected_patterns,
                        "leaked_data": evaluation_result.leaked_data,
                        "signal_breakdown": evaluation_result.signal_breakdown
                    },
                    "evaluation_metadata": {
                        "layer_used": evaluation_result.evaluation_layer.value,
                        "false_positive_checked": evaluation_result.false_positive_checked
                    }
                })

                if not evaluation_result.data_extraction_successful:
                    successful_resistances += 1
                else:
                    failed_extractions += 1

            except Exception as e:
                print(f"❌ Failed to evaluate response {i+1}: {e}")
                import traceback
                print(f"📋 Traceback:\n{traceback.format_exc()}")
                # Fallback to basic evaluation if new evaluator fails
                evaluated_responses.append({
                    **captured,
                    "data_extraction_successful": False,
                    "extraction_successful": False,
                    "confidence_score": 0.5,
                    "safety_score": 0.5,
                    "reasoning": f"Evaluation error: {str(e)}",
                    "evaluation": {"error": str(e)}
                })
                successful_resistances += 1  # Conservative: assume resistance if evaluation fails
                continue
        
        # Finalize results
        session["progress"] = 95
        detection_rate = (successful_resistances / len(evaluated_responses)) * 100 if evaluated_responses else 0

        print(f"✅ Evaluation completed: {successful_resistances} resistances, {failed_extractions} extractions")

        # Calculate total execution time correctly
        end_time = datetime.now()
        start_time_dt = datetime.fromisoformat(session["start_time"])
        total_execution_time = (end_time - start_time_dt).total_seconds()
        
        session["evaluated_responses"] = evaluated_responses
        session["results"] = {
            "detection_rate": detection_rate,
            "successful_resistances": successful_resistances,
            "failed_extractions": failed_extractions,
            "successful_captures": len(captured_responses),
            "successful_evaluations": len(evaluated_responses),
            "total_execution_time": total_execution_time,
            "performance_metrics": {
                "average_response_time": sum(r.get('response_time', 0) for r in captured_responses) / len(captured_responses) if captured_responses else 0,
                "total_api_calls": len(captured_responses),
                "total_execution_time": total_execution_time
            }
        }

        session["status"] = "completed"
        session["progress"] = 100
        session["completed_tests"] = len(evaluated_responses)
        session["current_step"] = "Test completed successfully!"
        session["end_time"] = end_time.isoformat()
        
        # Record analytics
        try:
            eval_client, judge_model = get_evaluation_client()
            analytics_service = AnalyticsService()
            await analytics_service.record_test_run(
                test_id=test_id,
                test_type="data_extraction",
                session=session,
                captured_responses=captured_responses,
                evaluated_responses=evaluated_responses,
                target_model=TARGET_MODEL,
                judge_model=judge_model,
            )
            print(f"✅ Analytics recorded for test {test_id}")
        except Exception as analytics_error:
            print(f"⚠️ Warning: Could not record analytics: {analytics_error}")
        
        print(f"✅ Data extraction test {test_id} completed successfully")
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        session["status"] = "failed"
        session["error"] = str(e)
        session["current_step"] = f"Test failed: {str(e)}"
        print(f"❌ Data extraction test {test_id} failed: {e}")
        print(f"📋 Full traceback:\n{error_traceback}")

async def execute_adversarial_attacks_test(test_id: str, session: Dict[str, Any]) -> None:
    """Execute adversarial attacks test."""
    try:
        session["status"] = "running"
        session["current_step"] = "Loading adversarial attacks dataset..."
        session["progress"] = 5
        
        if not ADVERSARIAL_ATTACKS_DATASET.exists():
            raise Exception("Adversarial attacks dataset not found")
        
        with open(ADVERSARIAL_ATTACKS_DATASET, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        all_samples = dataset.get('adversarial_samples', [])
        limited_samples = all_samples[:MAX_PROMPTS_ADVERSARIAL]
        
        session["total_tests"] = len(limited_samples)
        session["current_step"] = f"Testing {len(limited_samples)} adversarial attack prompts..."
        session["progress"] = 10
        print(f"📊 Progress: {session['progress']}% - {session['current_step']}")
        
        # Capture responses
        client = AsyncOpenAI(api_key=API_KEY)
        captured_responses = []
        
        for i, sample in enumerate(limited_samples):
            progress = 15 + (i / len(limited_samples)) * 40
            session["progress"] = int(progress)
            session["completed_tests"] = i
            
            try:
                response_start = time.time()
                response = await client.chat.completions.create(
                    model=TARGET_MODEL,
                    messages=[
                        {"role": "system", "content": sample.get('base_prompt', 'You are a helpful AI assistant.')},
                        {"role": "user", "content": sample.get('adversarial_prompt', '')}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                response_time = time.time() - response_start
                
                # Extract token usage
                token_usage = extract_token_usage(response)
                
                captured_responses.append({
                    "sample_id": sample.get('sample_id', f'adv_{i+1:03d}'),
                    "category": sample.get('category', 'unknown'),
                    "technique": sample.get('technique', 'unknown'),
                    "severity": sample.get('severity', 'unknown'),
                    "risk_category": sample.get('risk_category', 'unknown'),
                    "language": sample.get('language', 'English'),
                    "base_prompt": sample.get('base_prompt', ''),
                    "adversarial_prompt": sample.get('adversarial_prompt', ''),
                    "model_response": response.choices[0].message.content,
                    "response_time": response_time,
                    "api_model": TARGET_MODEL,
                    "capture_success": True,
                    "token_usage": token_usage,
                    "usage": token_usage  # Also store as 'usage' for compatibility
                })
            except Exception as e:
                print(f"❌ Failed to capture response {i+1}: {e}")
                import traceback
                print(f"📋 Traceback:\n{traceback.format_exc()}")
                continue
        
        session["captured_responses"] = captured_responses
        print(f"✅ Captured {len(captured_responses)} responses")

        # Initialize new multi-layer evaluator
        print(f"🔧 Initializing adversarial attacks evaluator for test: {test_id}")
        try:
            evaluator = create_adversarial_attacks_evaluator_with_defaults()
            print(f"✅ Evaluator created, initializing...")
            await evaluator.initialize()
            print(f"✅ Evaluator initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize evaluator: {e}")
            import traceback
            print(f"📋 Traceback:\n{traceback.format_exc()}")
            raise

        eval_provider = "Multi-Layer Evaluation (Layer 1 + Layer 3)"
        session["current_step"] = f"Evaluating responses with {eval_provider}..."
        session["progress"] = 60
        print(f"📊 Progress: {session['progress']}% - {session['current_step']}")

        # Evaluate responses using new multi-layer system
        evaluated_responses = []
        successful_resistances = 0
        failed_attacks = 0

        for i, captured in enumerate(captured_responses):
            progress = 60 + (i / len(captured_responses)) * 35
            session["progress"] = int(progress)
            session["current_step"] = f"Evaluating response {i+1}/{len(captured_responses)}"

            try:
                # Create evaluation context
                context = AdversarialAttacksEvaluationContext(
                    adversarial_prompt=captured.get('adversarial_prompt', ''),
                    model_response=captured.get('model_response', ''),
                    base_prompt=captured.get('base_prompt', ''),
                    judge_question=None,  # Will use default from evaluator
                    sample_metadata={
                        'sample_id': captured.get('sample_id', ''),
                        'category': captured.get('category', 'unknown'),
                        'technique': captured.get('technique', 'unknown'),
                        'severity': captured.get('severity', 'medium'),
                        'risk_category': captured.get('risk_category', 'unknown'),
                        'language': captured.get('language', 'English')
                    },
                    response_time=captured.get('response_time', 0.0)
                )

                # Track evaluation time
                evaluation_start = time.time()

                # Evaluate using new multi-layer system
                evaluation_result = await evaluator.evaluate(context)

                evaluation_time = time.time() - evaluation_start

                # Convert to format compatible with existing code
                evaluated_responses.append({
                    **captured,
                    "adversarial_impact": evaluation_result.adversarial_impact,
                    "confidence_score": evaluation_result.confidence_score,
                    "safety_score": evaluation_result.safety_score,
                    "robustness_score": evaluation_result.robustness_score,
                    "severity": evaluation_result.severity.value,
                    "reasoning": evaluation_result.reasoning,
                    "response_time": captured.get('response_time', 0.0),  # API call time
                    "evaluation_time": evaluation_time,  # Evaluation processing time
                    "evaluation": {
                        "adversarial_impact": evaluation_result.adversarial_impact,
                        "confidence_score": evaluation_result.confidence_score,
                        "severity": evaluation_result.severity.value,
                        "safety_score": evaluation_result.safety_score,
                        "robustness_score": evaluation_result.robustness_score,
                        "reasoning": evaluation_result.reasoning,
                        "evaluation_layer": evaluation_result.evaluation_layer.value,
                        "outcome": evaluation_result.outcome.value,
                        "detected_patterns": evaluation_result.detected_patterns,
                        "signal_breakdown": evaluation_result.signal_breakdown
                    },
                    "evaluation_metadata": {
                        "layer_used": evaluation_result.evaluation_layer.value,
                        "false_positive_checked": evaluation_result.false_positive_checked
                    }
                })

                if not evaluation_result.adversarial_impact:
                    successful_resistances += 1
                else:
                    failed_attacks += 1

            except Exception as e:
                print(f"❌ Failed to evaluate response {i+1}: {e}")
                import traceback
                print(f"📋 Traceback:\n{traceback.format_exc()}")
                # Fallback to basic evaluation if new evaluator fails
                evaluated_responses.append({
                    **captured,
                    "adversarial_impact": False,
                    "confidence_score": 0.5,
                    "safety_score": 0.5,
                    "robustness_score": 0.5,
                    "reasoning": f"Evaluation error: {str(e)}",
                    "evaluation": {"error": str(e)}
                })
                successful_resistances += 1  # Conservative: assume resistance if evaluation fails
                continue
        
        # Finalize results
        session["progress"] = 95
        robustness_rate = (successful_resistances / len(evaluated_responses)) * 100 if evaluated_responses else 0

        print(f"✅ Evaluation completed: {successful_resistances} resistances, {failed_attacks} attacks succeeded")

        # Calculate total execution time correctly
        end_time = datetime.now()
        start_time_dt = datetime.fromisoformat(session["start_time"])
        total_execution_time = (end_time - start_time_dt).total_seconds()
        
        session["evaluated_responses"] = evaluated_responses
        session["results"] = {
            "robustness_rate": robustness_rate,
            "successful_resistances": successful_resistances,
            "failed_attacks": failed_attacks,
            "successful_captures": len(captured_responses),
            "successful_evaluations": len(evaluated_responses),
            "total_execution_time": total_execution_time,
            "performance_metrics": {
                "average_response_time": sum(r.get('response_time', 0) for r in captured_responses) / len(captured_responses) if captured_responses else 0,
                "total_api_calls": len(captured_responses),
                "total_execution_time": total_execution_time
            }
        }

        session["status"] = "completed"
        session["progress"] = 100
        session["completed_tests"] = len(evaluated_responses)
        session["current_step"] = "Test completed successfully!"
        session["end_time"] = end_time.isoformat()
        
        # Record analytics
        try:
            eval_client, judge_model = get_evaluation_client()
            analytics_service = AnalyticsService()
            await analytics_service.record_test_run(
                test_id=test_id,
                test_type="adversarial_attacks",
                session=session,
                captured_responses=captured_responses,
                evaluated_responses=evaluated_responses,
                target_model=TARGET_MODEL,
                judge_model=judge_model,
            )
            print(f"✅ Analytics recorded for test {test_id}")
        except Exception as analytics_error:
            print(f"⚠️ Warning: Could not record analytics: {analytics_error}")
        
        print(f"✅ Adversarial attacks test {test_id} completed successfully")
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        session["status"] = "failed"
        session["error"] = str(e)
        session["current_step"] = f"Test failed: {str(e)}"
        print(f"❌ Adversarial attacks test {test_id} failed: {e}")
        print(f"📋 Full traceback:\n{error_traceback}")

