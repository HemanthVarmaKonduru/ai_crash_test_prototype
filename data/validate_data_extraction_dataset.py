#!/usr/bin/env python3
"""
Validate the data extraction dataset for completeness and quality.
"""

import json
import sys
from collections import Counter

def validate_dataset():
    """Validate the data extraction dataset."""
    
    # Load the dataset
    with open('/Users/hv/Desktop/Hemanth/AI/AI_Projects_Karun/ai_crash_test_prototype/data/data_extraction_comprehensive.json', 'r') as f:
        dataset = json.load(f)
    
    print("🔍 Validating Data Extraction Dataset...")
    print("=" * 50)
    
    # Check metadata
    metadata = dataset["metadata"]
    print(f"📊 Dataset: {metadata['dataset_name']}")
    print(f"📅 Created: {metadata['created_date']}")
    print(f"📝 Description: {metadata['description']}")
    print(f"🔢 Total Samples: {metadata['total_samples']}")
    print(f"🌍 Languages: {metadata['languages_covered']}")
    print(f"⚔️  Techniques: {metadata['attack_techniques']}")
    
    # Validate samples
    samples = dataset["data_extraction_samples"]
    print(f"\n✅ Sample Count: {len(samples)}")
    
    # Check for required fields
    required_fields = [
        "sample_id", "category", "technique", "severity", "risk_category",
        "language", "base_prompt", "extraction_prompt", "expected_behavior",
        "judge_question", "success_criteria", "variants", "multilingual_variants",
        "defense_evasion_techniques", "testing_metadata"
    ]
    
    missing_fields = []
    for i, sample in enumerate(samples):
        for field in required_fields:
            if field not in sample:
                missing_fields.append(f"Sample {i+1} ({sample.get('sample_id', 'unknown')}): missing {field}")
    
    if missing_fields:
        print(f"\n❌ Missing Fields Found:")
        for field in missing_fields:
            print(f"   - {field}")
    else:
        print(f"\n✅ All required fields present in all samples")
    
    # Check severity distribution
    severities = [sample["severity"] for sample in samples]
    severity_counts = Counter(severities)
    print(f"\n📊 Severity Distribution:")
    for severity, count in severity_counts.items():
        print(f"   {severity.capitalize()}: {count} samples ({count/len(samples)*100:.1f}%)")
    
    # Check risk category distribution
    risk_categories = [sample["risk_category"] for sample in samples]
    risk_counts = Counter(risk_categories)
    print(f"\n📊 Risk Category Distribution:")
    for category, count in risk_counts.items():
        print(f"   {category}: {count} samples ({count/len(samples)*100:.1f}%)")
    
    # Check language distribution
    languages = [sample["language"] for sample in samples]
    language_counts = Counter(languages)
    print(f"\n📊 Language Distribution:")
    for language, count in language_counts.items():
        print(f"   {language}: {count} samples ({count/len(samples)*100:.1f}%)")
    
    # Check technique distribution
    techniques = [sample["technique"] for sample in samples]
    technique_counts = Counter(techniques)
    print(f"\n📊 Technique Distribution:")
    for technique, count in technique_counts.items():
        print(f"   {technique}: {count} samples")
    
    # Check sample IDs are unique
    sample_ids = [sample["sample_id"] for sample in samples]
    if len(sample_ids) == len(set(sample_ids)):
        print(f"\n✅ All sample IDs are unique")
    else:
        print(f"\n❌ Duplicate sample IDs found")
    
    # Check sample ID format
    invalid_ids = []
    for sample_id in sample_ids:
        if not sample_id.startswith("de_") or not sample_id[3:].isdigit():
            invalid_ids.append(sample_id)
    
    if invalid_ids:
        print(f"\n❌ Invalid sample ID format: {invalid_ids}")
    else:
        print(f"\n✅ All sample IDs follow correct format (de_XXX)")
    
    # Check multilingual variants
    multilingual_coverage = 0
    for sample in samples:
        if sample["multilingual_variants"] and len(sample["multilingual_variants"]) > 0:
            multilingual_coverage += 1
    
    print(f"\n🌍 Multilingual Coverage: {multilingual_coverage}/{len(samples)} samples ({multilingual_coverage/len(samples)*100:.1f}%)")
    
    # Check testing metadata
    metadata_issues = []
    for i, sample in enumerate(samples):
        testing_metadata = sample.get("testing_metadata", {})
        required_metadata = ["difficulty", "success_rate", "false_positive_rate", "recovery_time", "data_sensitivity"]
        
        for field in required_metadata:
            if field not in testing_metadata:
                metadata_issues.append(f"Sample {i+1} ({sample.get('sample_id', 'unknown')}): missing {field}")
    
    if metadata_issues:
        print(f"\n❌ Testing Metadata Issues:")
        for issue in metadata_issues:
            print(f"   - {issue}")
    else:
        print(f"\n✅ All testing metadata fields present")
    
    # Check success rates are reasonable
    success_rate_issues = []
    for i, sample in enumerate(samples):
        testing_metadata = sample.get("testing_metadata", {})
        success_rate = testing_metadata.get("success_rate", 0)
        if not (0 <= success_rate <= 1):
            success_rate_issues.append(f"Sample {i+1} ({sample.get('sample_id', 'unknown')}): invalid success_rate {success_rate}")
    
    if success_rate_issues:
        print(f"\n❌ Success Rate Issues:")
        for issue in success_rate_issues:
            print(f"   - {issue}")
    else:
        print(f"\n✅ All success rates are valid (0-1 range)")
    
    # Summary
    print(f"\n" + "=" * 50)
    if not missing_fields and not invalid_ids and not metadata_issues and not success_rate_issues:
        print("🎉 Dataset validation PASSED - Ready for production use!")
        return True
    else:
        print("❌ Dataset validation FAILED - Issues need to be fixed")
        return False

if __name__ == "__main__":
    success = validate_dataset()
    sys.exit(0 if success else 1)
