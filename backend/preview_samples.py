#!/usr/bin/env python3
"""
Preview the first 20 samples from crash_test_prompts.jsonl without calling the API
"""
import json
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.models.prompt import Prompt, PromptCategory, PromptDifficulty, ExpectedBehavior


def preview_sample_prompts(file_path: str, limit: int = 20):
    """Preview first N prompts from the JSONL file"""
    prompts = []
    
    print(f"📂 Previewing first {limit} prompts from {file_path}...")
    
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
                print(f"⚠️  Error parsing line {i}: {e}")
                continue
    
    print(f"✅ Loaded {len(prompts)} prompts")
    return prompts


def main():
    """Preview sample prompts"""
    print("🔍 AI Crash Test Prototype - Sample Preview")
    print("=" * 50)
    
    # Load sample prompts
    prompts = preview_sample_prompts("crash_test_prompts.jsonl", limit=20)
    
    if not prompts:
        print("❌ No prompts loaded!")
        return
    
    # Show statistics
    print(f"\n📊 Sample Statistics:")
    print("-" * 30)
    
    categories = {}
    difficulties = {}
    behaviors = {}
    
    for prompt in prompts:
        # Category stats
        cat = prompt.category if isinstance(prompt.category, str) else prompt.category.value
        categories[cat] = categories.get(cat, 0) + 1
        
        # Difficulty stats
        diff = prompt.difficulty if isinstance(prompt.difficulty, str) else prompt.difficulty.value
        difficulties[diff] = difficulties.get(diff, 0) + 1
        
        # Behavior stats
        beh = prompt.expected_behavior if isinstance(prompt.expected_behavior, str) else prompt.expected_behavior.value
        behaviors[beh] = behaviors.get(beh, 0) + 1
    
    print("Categories:")
    for cat, count in categories.items():
        print(f"  {cat}: {count}")
    
    print("\nDifficulties:")
    for diff, count in difficulties.items():
        print(f"  {diff}: {count}")
    
    print("\nExpected Behaviors:")
    for beh, count in behaviors.items():
        print(f"  {beh}: {count}")
    
    # Show detailed prompts
    print(f"\n📝 Detailed Prompts ({len(prompts)} total):")
    print("=" * 50)
    
    for i, prompt in enumerate(prompts):
        print(f"\n{i+1}. {prompt.title}")
        print(f"   ID: {prompt.id}")
        print(f"   Category: {prompt.category if isinstance(prompt.category, str) else prompt.category.value}")
        print(f"   Difficulty: {prompt.difficulty if isinstance(prompt.difficulty, str) else prompt.difficulty.value}")
        print(f"   Expected Behavior: {prompt.expected_behavior if isinstance(prompt.expected_behavior, str) else prompt.expected_behavior.value}")
        print(f"   Source: {prompt.source}")
        print(f"   Content: {prompt.content[:200]}...")
        
        if prompt.metadata:
            print(f"   Metadata: {prompt.metadata}")
        
        print("-" * 30)
    
    print(f"\n🎉 Preview completed! Found {len(prompts)} sample prompts.")
    print("\nTo run actual tests, set your OpenAI API key:")
    print("export OPENAI_API_KEY='your_key_here'")
    print("Then run: python test_with_samples.py")


if __name__ == "__main__":
    main()
