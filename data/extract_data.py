#!/usr/bin/env python3
"""
Extract data from Anthropic HH-RLHF dataset and save as CSV files
"""
import pandas as pd
from datasets import load_dataset
import re

def clean_text(text):
    """Clean and format text for better readability"""
    if not text:
        return ""
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_prompt_and_response(conversation):
    """Extract prompt and response from conversation format"""
    if not conversation:
        return "", ""
    
    # Split by "Human:" and "Assistant:"
    parts = re.split(r'\n\nHuman:|\n\nAssistant:', conversation)
    
    if len(parts) >= 3:
        prompt = clean_text(parts[1])  # Human part
        response = clean_text(parts[2])  # Assistant part
        return prompt, response
    
    return "", ""

def process_dataset():
    """Load and process the HH-RLHF dataset"""
    print("Loading Anthropic HH-RLHF dataset...")
    ds = load_dataset("Anthropic/hh-rlhf")
    
    print(f"Dataset loaded successfully!")
    print(f"Train data: {len(ds['train'])} rows")
    print(f"Test data: {len(ds['test'])} rows")
    
    # Process training data
    print("\nProcessing training data...")
    train_data = []
    
    for i, item in enumerate(ds['train']):
        if i % 10000 == 0:
            print(f"Processed {i}/{len(ds['train'])} training samples...")
        
        # Extract prompt and responses
        chosen_prompt, chosen_response = extract_prompt_and_response(item['chosen'])
        rejected_prompt, rejected_response = extract_prompt_and_response(item['rejected'])
        
        # Create entries for both chosen and rejected responses
        train_data.append({
            'id': f"train_{i}_chosen",
            'title': f"Training Sample {i} (Chosen)",
            'content': chosen_prompt,
            'category': 'conversation',
            'difficulty': 'medium',
            'expected_output': chosen_response,
            'response_type': 'chosen'
        })
        
        train_data.append({
            'id': f"train_{i}_rejected", 
            'title': f"Training Sample {i} (Rejected)",
            'content': rejected_prompt,
            'category': 'conversation',
            'difficulty': 'medium',
            'expected_output': rejected_response,
            'response_type': 'rejected'
        })
    
    # Process test data
    print("\nProcessing test data...")
    test_data = []
    
    for i, item in enumerate(ds['test']):
        if i % 1000 == 0:
            print(f"Processed {i}/{len(ds['test'])} test samples...")
        
        # Extract prompt and responses
        chosen_prompt, chosen_response = extract_prompt_and_response(item['chosen'])
        rejected_prompt, rejected_response = extract_prompt_and_response(item['rejected'])
        
        # Create entries for both chosen and rejected responses
        test_data.append({
            'id': f"test_{i}_chosen",
            'title': f"Test Sample {i} (Chosen)",
            'content': chosen_prompt,
            'category': 'conversation',
            'difficulty': 'medium',
            'expected_output': chosen_response,
            'response_type': 'chosen'
        })
        
        test_data.append({
            'id': f"test_{i}_rejected",
            'title': f"Test Sample {i} (Rejected)", 
            'content': rejected_prompt,
            'category': 'conversation',
            'difficulty': 'medium',
            'expected_output': rejected_response,
            'response_type': 'rejected'
        })
    
    # Convert to DataFrames and save
    print("\nSaving data to CSV files...")
    
    train_df = pd.DataFrame(train_data)
    test_df = pd.DataFrame(test_data)
    
    # Save training data
    train_df.to_csv('data/train_data.csv', index=False)
    print(f"✓ Saved {len(train_df)} training samples to data/train_data.csv")
    
    # Save test data
    test_df.to_csv('data/test_data.csv', index=False)
    print(f"✓ Saved {len(test_df)} test samples to data/test_data.csv")
    
    # Save a sample for quick testing (first 100 samples)
    sample_df = train_df.head(100)
    sample_df.to_csv('data/sample_data.csv', index=False)
    print(f"✓ Saved {len(sample_df)} sample records to data/sample_data.csv")
    
    # Print summary
    print(f"\n📊 Data Summary:")
    print(f"Total training samples: {len(train_df)}")
    print(f"Total test samples: {len(test_df)}")
    print(f"Sample data for testing: {len(sample_df)}")
    
    # Show sample of the data
    print(f"\n📝 Sample data preview:")
    print(sample_df[['title', 'content', 'expected_output']].head(3).to_string())

if __name__ == "__main__":
    process_dataset()
