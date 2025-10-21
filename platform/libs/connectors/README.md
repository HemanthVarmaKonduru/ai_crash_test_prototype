# Connectors Library

Model provider connectors for the Adversarial Sandbox platform.

## Overview

This library provides standardized interfaces for connecting to various LLM providers. Each connector implements a common interface for model testing, API calls, and response normalization.

## Supported Providers

- **OpenAI** - GPT-3.5-turbo, GPT-4, and other OpenAI models
- **Anthropic** - Claude models (planned)
- **HuggingFace** - Open-source models (planned)

## Usage

### Basic Connection Test

```python
from connectors import OpenAIConnector

# Initialize connector
connector = OpenAIConnector(
    api_key="your-openai-api-key",
    model="gpt-3.5-turbo"
)

# Test connection
result = await connector.test_connection()
if result.status == ConnectionStatus.SUCCESS:
    print(f"Connected! Latency: {result.latency_ms}ms")
else:
    print(f"Connection failed: {result.message}")
```

### Sending Prompts

```python
# Send a prompt
response = await connector.send_prompt(
    prompt="What is adversarial testing?",
    system_message="You are a security expert.",
    temperature=0.7,
    max_tokens=500
)

print(f"Response: {response.content}")
print(f"Usage: {response.usage}")
print(f"Latency: {response.latency_ms}ms")
```

## Architecture

### Base Connector Interface

All connectors implement the `BaseConnector` interface:

- `test_connection()` - Verify API connectivity
- `send_prompt()` - Send prompts and get responses  
- `get_model_info()` - Get model metadata
- `provider_name` - Provider identifier

### Standardized Responses

- `ConnectionResult` - Connection test results
- `ModelResponse` - Standardized model responses
- `ConnectionStatus` - Status enumeration

## Development

### Installation

```bash
cd platform/libs/connectors
pip install -e .
```

### Testing

```bash
pytest tests/
```

### Code Quality

```bash
black src/
isort src/
flake8 src/
```

