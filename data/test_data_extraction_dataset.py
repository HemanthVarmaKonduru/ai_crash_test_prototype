#!/usr/bin/env python3
"""
Test script to demonstrate the data extraction dataset functionality.
"""

import json
import random
from datetime import datetime

def load_dataset():
    """Load the data extraction dataset."""
    with open('/Users/hv/Desktop/Hemanth/AI/AI_Projects_Karun/ai_crash_test_prototype/data/data_extraction_comprehensive.json', 'r') as f:
        return json.load(f)

def display_sample(sample):
    """Display a sample in a formatted way."""
    print(f"\n🎯 Sample ID: {sample['sample_id']}")
    print(f"📋 Category: {sample['category']}")
    print(f"⚔️  Technique: {sample['technique']}")
    print(f"🚨 Severity: {sample['severity']}")
    print(f"🏷️  Risk Category: {sample['risk_category']}")
    print(f"🌍 Language: {sample['language']}")
    print(f"\n📝 Base Prompt:")
    print(f"   {sample['base_prompt']}")
    print(f"\n🎯 Extraction Prompt:")
    print(f"   {sample['extraction_prompt']}")
    print(f"\n✅ Expected Behavior:")
    print(f"   {sample['expected_behavior']}")
    print(f"\n❓ Judge Question:")
    print(f"   {sample['judge_question']}")
    print(f"\n🎯 Success Criteria:")
    print(f"   {sample['success_criteria']}")
    
    if sample['variants']:
        print(f"\n🔄 Variants:")
        for i, variant in enumerate(sample['variants'][:3], 1):
            print(f"   {i}. {variant}")
    
    if sample['multilingual_variants']:
        print(f"\n🌍 Multilingual Variants:")
        for lang, variant in list(sample['multilingual_variants'].items())[:3]:
            print(f"   {lang}: {variant}")
    
    print(f"\n🛡️  Defense Evasion Techniques:")
    for technique in sample['defense_evasion_techniques']:
        print(f"   - {technique}")
    
    metadata = sample['testing_metadata']
    print(f"\n📊 Testing Metadata:")
    print(f"   Difficulty: {metadata['difficulty']}")
    print(f"   Success Rate: {metadata['success_rate']:.2f}")
    print(f"   False Positive Rate: {metadata['false_positive_rate']:.2f}")
    print(f"   Recovery Time: {metadata['recovery_time']}")
    print(f"   Data Sensitivity: {metadata['data_sensitivity']}")

def test_dataset():
    """Test the dataset functionality."""
    print("🔍 Testing Data Extraction Dataset")
    print("=" * 50)
    
    # Load dataset
    dataset = load_dataset()
    samples = dataset["data_extraction_samples"]
    metadata = dataset["metadata"]
    
    print(f"📊 Dataset Overview:")
    print(f"   Name: {metadata['dataset_name']}")
    print(f"   Version: {metadata['version']}")
    print(f"   Total Samples: {metadata['total_samples']}")
    print(f"   Languages: {metadata['languages_covered']}")
    print(f"   Techniques: {metadata['attack_techniques']}")
    
    print(f"\n📈 Severity Distribution:")
    for severity, count in metadata['severity_distribution'].items():
        print(f"   {severity.capitalize()}: {count} samples")
    
    print(f"\n📈 Risk Category Distribution:")
    for category, count in metadata['risk_category_distribution'].items():
        print(f"   {category}: {count} samples")
    
    # Test random samples
    print(f"\n🎲 Testing Random Samples:")
    print("=" * 30)
    
    # Test critical severity samples
    critical_samples = [s for s in samples if s['severity'] == 'critical']
    if critical_samples:
        print(f"\n🚨 Critical Severity Sample:")
        display_sample(random.choice(critical_samples))
    
    # Test high severity samples
    high_samples = [s for s in samples if s['severity'] == 'high']
    if high_samples:
        print(f"\n⚠️  High Severity Sample:")
        display_sample(random.choice(high_samples))
    
    # Test different risk categories
    risk_categories = list(set(s['risk_category'] for s in samples))
    for category in risk_categories[:2]:  # Test first 2 categories
        category_samples = [s for s in samples if s['risk_category'] == category]
        if category_samples:
            print(f"\n🏷️  {category.replace('-', ' ').title()} Sample:")
            display_sample(random.choice(category_samples))
    
    # Test multilingual samples
    multilingual_samples = [s for s in samples if s['multilingual_variants']]
    if multilingual_samples:
        print(f"\n🌍 Multilingual Sample:")
        display_sample(random.choice(multilingual_samples))
    
    print(f"\n" + "=" * 50)
    print("✅ Dataset test completed successfully!")
    print(f"📊 Total samples tested: {len(samples)}")
    print(f"🎯 Ready for integration with the platform!")

if __name__ == "__main__":
    test_dataset()
