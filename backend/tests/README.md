# Backend Tests

This directory contains comprehensive unit and integration tests for the backend services.

## ⚠️ Important Note About API Calls

**The test suite does NOT make actual API calls to GPT-3.5-turbo or other target models.**

- **Unit/Integration Tests**: Use mock/hardcoded model responses to test evaluation logic
- **Real API Calls**: Happen in `backend/services/test_executor.py` during normal execution
  - The test executor makes real calls to GPT-3.5-turbo to get actual model responses
  - Then uses the evaluation system to analyze those real responses

**Why?** 
- Tests should be fast and not depend on external APIs
- Tests validate logic, not API connectivity
- Real API testing happens when you run actual test executions

## Test Structure

```
tests/
├── services/
│   └── prompt_injection/
│       ├── test_layer1_semantic.py          # Semantic similarity analyzer tests
│       ├── test_layer1_structural.py        # Structural pattern analyzer tests
│       ├── test_signal_aggregator.py        # Signal aggregation tests
│       ├── test_confidence_calculator.py   # Confidence calculation tests
│       ├── test_false_positive_detector.py  # False positive detection tests
│       ├── test_evaluator_integration.py    # Main evaluator integration tests
│       └── test_dataset_integration.py        # Real dataset integration tests
```

## Running Tests

### Run all tests:
```bash
cd backend
pytest tests/ -v
```

### Run specific test file:
```bash
pytest tests/services/prompt_injection/test_layer1_semantic.py -v
```

### Run with markers:
```bash
# Only integration tests
pytest tests/ -m integration -v

# Only unit tests
pytest tests/ -m unit -v

# Skip slow tests
pytest tests/ -m "not slow" -v
```

### Run with coverage:
```bash
pytest tests/ --cov=backend/services/prompt_injection --cov-report=html
```

## Test Data

Tests use the dataset from `data/prompt_injection_limited_30.json` for integration tests.

## Requirements

Install test dependencies:
```bash
pip install pytest pytest-asyncio
```

## Test Markers

- `@pytest.mark.asyncio`: Async tests
- `@pytest.mark.integration`: Integration tests (use real data)
- `@pytest.mark.unit`: Unit tests (isolated components)
- `@pytest.mark.slow`: Slow running tests

