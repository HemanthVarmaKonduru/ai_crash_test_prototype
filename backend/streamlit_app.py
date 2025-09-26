#!/usr/bin/env python3
"""
Streamlit frontend for AI Crash Test Prototype
"""
import streamlit as st
import json
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.plugins import PluginManager
from src.plugins.models.openai_model import OpenAIModel
from src.plugins.evaluators.safety_evaluator import SafetyEvaluator
from src.models.config import ModelConfig, EvaluationConfig
from src.core.testing.test_runner import TestRunner
from src.models.prompt import Prompt, PromptCategory, PromptDifficulty, ExpectedBehavior


def load_prompts_from_file(file_path: str, limit: int = 20):
    """Load prompts from the JSONL file"""
    prompts = []
    
    try:
        with open(file_path, 'r') as f:
            for i, line in enumerate(f):
                if i >= limit:
                    break
                
                try:
                    data = json.loads(line.strip())
                    
                    # Convert to our Prompt model
                    prompt = Prompt(
                        id=data.get('id', f'sample_{i}'),
                        title=data.get('title', f'Sample {i}'),
                        content=data.get('prompt', ''),
                        category=PromptCategory(data.get('category', 'general')),
                        difficulty=PromptDifficulty(data.get('difficulty', 'medium')),
                        expected_behavior=ExpectedBehavior(data.get('expected_behavior', 'safe_explanation')),
                        source=data.get('source', 'crash_test_prompts'),
                        metadata=data.get('metadata', {})
                    )
                    prompts.append(prompt)
                    
                except Exception as e:
                    st.warning(f"Error parsing line {i}: {e}")
                    continue
        
        return prompts
        
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        return []
    except Exception as e:
        st.error(f"Error loading prompts: {e}")
        return []


async def run_crash_tests(api_key: str, prompts: list, model_name: str = "gpt-3.5-turbo"):
    """Run crash tests with the given prompts"""
    
    # Initialize plugin manager
    plugin_manager = PluginManager()
    plugin_manager.register_model("openai", OpenAIModel)
    plugin_manager.register_evaluator("safety", SafetyEvaluator)
    
    # Create configurations
    model_config = ModelConfig(
        name=model_name,
        provider="openai",
        api_key=api_key,
        max_tokens=150,
        temperature=0.7
    )
    
    evaluator_config = EvaluationConfig(
        evaluator_name="safety",
        strict_mode=False
    )
    
    try:
        # Create instances
        model = plugin_manager.create_model("openai", model_config.model_dump())
        evaluator = plugin_manager.create_evaluator("safety", evaluator_config.model_dump())
        
        # Create test runner
        test_runner = TestRunner(model, evaluator)
        
        # Run health check
        health = await model.health_check()
        if not health:
            return None, "Model health check failed"
        
        # Run tests
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, prompt in enumerate(prompts):
            status_text.text(f"Testing prompt {i+1}/{len(prompts)}: {prompt.title}")
            
            try:
                result = await test_runner.run_single_test(prompt)
                results.append(result)
            except Exception as e:
                st.warning(f"Error testing prompt {i+1}: {e}")
                continue
            
            progress_bar.progress((i + 1) / len(prompts))
        
        status_text.text("Testing completed!")
        return results, None
        
    except Exception as e:
        return None, str(e)


def main():
    """Main Streamlit app"""
    st.set_page_config(
        page_title="AI Crash Test Prototype",
        page_icon="🧪",
        layout="wide"
    )
    
    st.title("🧪 AI Crash Test Prototype")
    st.markdown("Test AI models with safety prompts and evaluate their responses")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key to test the model"
        )
        
        # Model selection
        model_name = st.selectbox(
            "Model",
            ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            index=0
        )
        
        # Number of prompts to test
        num_prompts = st.slider(
            "Number of prompts to test",
            min_value=1,
            max_value=100,
            value=10,
            help="Select how many prompts from the crash test dataset to evaluate"
        )
        
        # Test button
        run_tests = st.button("🚀 Run Crash Tests", type="primary")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📊 Test Results")
        
        if run_tests:
            if not api_key:
                st.error("Please enter your OpenAI API key in the sidebar")
                return
            
            # Load prompts
            with st.spinner("Loading prompts..."):
                prompts = load_prompts_from_file("crash_test_prompts.jsonl", num_prompts)
            
            if not prompts:
                st.error("No prompts loaded. Please check if crash_test_prompts.jsonl exists.")
                return
            
            st.success(f"Loaded {len(prompts)} prompts for testing")
            
            # Run tests
            with st.spinner("Running crash tests..."):
                results, error = asyncio.run(run_crash_tests(api_key, prompts, model_name))
            
            if error:
                st.error(f"Error running tests: {error}")
                return
            
            if not results:
                st.warning("No results returned")
                return
            
            # Display results
            st.success(f"✅ Completed testing {len(results)} prompts")
            
            # Summary statistics
            total = len(results)
            passed = sum(1 for r in results if (r.status.value if hasattr(r.status, 'value') else r.status) == "PASS")
            failed = sum(1 for r in results if (r.status.value if hasattr(r.status, 'value') else r.status) == "FAIL")
            unknown = sum(1 for r in results if (r.status.value if hasattr(r.status, 'value') else r.status) == "UNKNOWN")
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Tests", total)
            with col2:
                st.metric("Passed", passed, f"{passed/total*100:.1f}%")
            with col3:
                st.metric("Failed", failed, f"{failed/total*100:.1f}%")
            with col4:
                st.metric("Unknown", unknown, f"{unknown/total*100:.1f}%")
            
            # Category breakdown
            st.subheader("📈 Results by Category")
            categories = {}
            for result in results:
                cat = result.category.value if result.category and hasattr(result.category, 'value') else (result.category if result.category else "unknown")
                if cat not in categories:
                    categories[cat] = {"total": 0, "passed": 0, "failed": 0}
                categories[cat]["total"] += 1
                status = result.status.value if hasattr(result.status, 'value') else result.status
                if status == "PASS":
                    categories[cat]["passed"] += 1
                elif status == "FAIL":
                    categories[cat]["failed"] += 1
            
            for cat, stats in categories.items():
                pass_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
                st.write(f"**{cat.title()}**: {stats['passed']}/{stats['total']} ({pass_rate:.1f}%)")
            
            # Safety flags summary
            st.subheader("🚩 Safety Flags Summary")
            if any(result.metadata and 'flags' in result.metadata for result in results):
                toxicity_count = sum(1 for r in results if r.metadata and r.metadata.get('flags', {}).get('toxicity', False))
                pii_count = sum(1 for r in results if r.metadata and r.metadata.get('flags', {}).get('pii', False))
                bias_count = sum(1 for r in results if r.metadata and r.metadata.get('flags', {}).get('bias', False))
                compliance_count = sum(1 for r in results if r.metadata and r.metadata.get('flags', {}).get('behavior_compliance', False))
                
                flag_col1, flag_col2, flag_col3, flag_col4 = st.columns(4)
                
                with flag_col1:
                    st.metric("Toxicity Detected", toxicity_count, f"{toxicity_count/total*100:.1f}%")
                
                with flag_col2:
                    st.metric("PII Detected", pii_count, f"{pii_count/total*100:.1f}%")
                
                with flag_col3:
                    st.metric("Bias Detected", bias_count, f"{bias_count/total*100:.1f}%")
                
                with flag_col4:
                    st.metric("Behavior Compliant", compliance_count, f"{compliance_count/total*100:.1f}%")
            else:
                st.info("No safety flags data available in results")
            
            # Detailed results
            st.subheader("📝 Detailed Results")
            
            for i, result in enumerate(results):
                with st.expander(f"Test {i+1}: {result.prompt_id[:8]}... - {result.status.value if hasattr(result.status, 'value') else result.status}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Category:**", result.category.value if result.category and hasattr(result.category, 'value') else result.category)
                        st.write("**Difficulty:**", result.difficulty.value if result.difficulty and hasattr(result.difficulty, 'value') else result.difficulty)
                        st.write("**Expected Behavior:**", result.expected_behavior)
                        st.write("**Evaluation Score:**", f"{result.evaluation_score:.2f}")
                    
                    with col2:
                        status_color = "🟢" if (result.status.value if hasattr(result.status, 'value') else result.status) == "PASS" else "🔴" if (result.status.value if hasattr(result.status, 'value') else result.status) == "FAIL" else "🟡"
                        st.write(f"**Status:** {status_color} {result.status.value if hasattr(result.status, 'value') else result.status}")
                    
                    # Display safety flags if available
                    if result.metadata and 'flags' in result.metadata:
                        st.subheader("🚩 Safety Flags")
                        flags = result.metadata['flags']
                        
                        flag_col1, flag_col2, flag_col3, flag_col4 = st.columns(4)
                        
                        with flag_col1:
                            toxicity_icon = "🔴" if flags.get('toxicity', False) else "🟢"
                            st.write(f"**Toxicity:** {toxicity_icon} {'Detected' if flags.get('toxicity', False) else 'Clean'}")
                        
                        with flag_col2:
                            pii_icon = "🔴" if flags.get('pii', False) else "🟢"
                            st.write(f"**PII:** {pii_icon} {'Detected' if flags.get('pii', False) else 'Clean'}")
                        
                        with flag_col3:
                            bias_icon = "🔴" if flags.get('bias', False) else "🟢"
                            st.write(f"**Bias:** {bias_icon} {'Detected' if flags.get('bias', False) else 'Clean'}")
                        
                        with flag_col4:
                            compliance_icon = "🟢" if flags.get('behavior_compliance', False) else "🔴"
                            st.write(f"**Compliance:** {compliance_icon} {'Compliant' if flags.get('behavior_compliance', False) else 'Non-compliant'}")
                    
                    st.write("**Model Response:**")
                    st.text_area("", result.model_response, height=100, key=f"response_{i}")
    
    with col2:
        st.header("📋 Dataset Info")
        
        # Show dataset statistics
        try:
            with open("crash_test_prompts.jsonl", 'r') as f:
                total_lines = sum(1 for _ in f)
            
            st.metric("Total Prompts Available", total_lines)
            
            # Show sample of categories
            st.subheader("📊 Sample Categories")
            sample_prompts = load_prompts_from_file("crash_test_prompts.jsonl", 100)
            
            if sample_prompts:
                categories = {}
                for prompt in sample_prompts:
                    cat = prompt.category.value if hasattr(prompt.category, 'value') else prompt.category
                    categories[cat] = categories.get(cat, 0) + 1
                
                for cat, count in categories.items():
                    st.write(f"• **{cat.title()}**: {count}")
            
        except FileNotFoundError:
            st.warning("crash_test_prompts.jsonl not found")
        
        st.subheader("ℹ️ About")
        st.info("""
        This tool tests AI models with challenging prompts to evaluate their safety and behavior.
        
        **Features:**
        - Tests multiple prompt categories
        - Evaluates model responses
        - Provides detailed analysis
        - Shows pass/fail rates
        """)


if __name__ == "__main__":
    main()


