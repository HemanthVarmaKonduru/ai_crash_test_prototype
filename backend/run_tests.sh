#!/bin/bash

# Test runner script for prompt injection evaluation module

echo "🧪 Running Prompt Injection Evaluation Tests"
echo "=============================================="
echo ""

# Change to backend directory
cd "$(dirname "$0")"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing..."
    pip install pytest pytest-asyncio
fi

# Run tests
echo "📋 Running all tests..."
pytest tests/services/prompt_injection/ -v --tb=short

echo ""
echo "✅ Test run complete!"

