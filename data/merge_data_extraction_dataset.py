#!/usr/bin/env python3
"""
Merge the main data extraction dataset with additional samples to create the complete 50-sample dataset.
"""

import json
from datetime import datetime

# Load the main dataset
with open('/Users/hv/Desktop/Hemanth/AI/AI_Projects_Karun/ai_crash_test_prototype/data/data_extraction_comprehensive.json', 'r') as f:
    main_dataset = json.load(f)

# Load additional samples
with open('/Users/hv/Desktop/Hemanth/AI/AI_Projects_Karun/ai_crash_test_prototype/data/data_extraction_additional_samples.json', 'r') as f:
    additional_samples = json.load(f)

# Add additional samples to the main dataset
main_dataset["data_extraction_samples"].extend(additional_samples)

# Update metadata
main_dataset["metadata"]["total_samples"] = len(main_dataset["data_extraction_samples"])
main_dataset["metadata"]["created_date"] = datetime.now().isoformat()

# Update severity distribution
severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
risk_category_counts = {
    "training-data-extraction": 0,
    "system-prompt-extraction": 0,
    "user-data-extraction": 0,
    "model-architecture-extraction": 0,
    "api-key-extraction": 0
}

for sample in main_dataset["data_extraction_samples"]:
    severity_counts[sample["severity"]] += 1
    risk_category_counts[sample["risk_category"]] += 1

main_dataset["metadata"]["severity_distribution"] = severity_counts
main_dataset["metadata"]["risk_category_distribution"] = risk_category_counts

# Save the complete dataset
with open('/Users/hv/Desktop/Hemanth/AI/AI_Projects_Karun/ai_crash_test_prototype/data/data_extraction_comprehensive.json', 'w') as f:
    json.dump(main_dataset, f, indent=2)

print(f"✅ Complete dataset created with {main_dataset['metadata']['total_samples']} samples")
print(f"📊 Severity distribution: {severity_counts}")
print(f"📊 Risk category distribution: {risk_category_counts}")
print("💾 Dataset saved to data_extraction_comprehensive.json")
