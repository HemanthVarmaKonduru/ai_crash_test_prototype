# AI Crash Test Prototype v2.0

A modular, extensible framework for testing AI model safety and behavior through crash testing.

## 🏗️ Architecture

This project uses a clean, modular architecture with:

- **🔌 Plugin System**: Easy to add new models, evaluators, datasets
- **📊 Type Safety**: Full Pydantic validation and type hints
- **⚙️ Configuration**: Environment-based configuration management
- **🌐 API**: Clean, versioned REST API
- **💻 CLI**: Command-line interface with plugin support
- **🧪 Testing**: Comprehensive test framework

## 📁 Project Structure

```
backend/
├── src/                    # Source code
│   ├── models/            # Data models & schemas
│   ├── interfaces/        # Abstract contracts
│   ├── plugins/           # Extensible implementations
│   │   ├── models/        # AI model plugins
│   │   ├── evaluators/    # Response evaluators
│   │   └── datasets/      # Dataset plugins
│   ├── core/             # Business logic
│   │   └── testing/      # Test execution
│   ├── config/           # Configuration management
│   ├── api/              # FastAPI application
│   │   └── v1/           # API version 1
│   └── cli/              # Command-line interface
├── main.py               # Application entry point
├── cli.py                # CLI entry point
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

### 3. Test the Architecture

```bash
python test_new_architecture.py
```

### 4. Run the API Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### 5. Use the CLI

```bash
# List available plugins
python cli.py list

# Run crash tests
python cli.py test --model gpt-3.5-turbo
```

## 🔌 Plugin System

### Models
- **OpenAI**: GPT-3.5, GPT-4, GPT-4-turbo
- **Extensible**: Easy to add Anthropic, Cohere, local models

### Evaluators
- **Safety**: Detects harmful content and safety violations
- **Extensible**: Easy to add bias, privacy, custom evaluators

### Datasets
- **Anthropic HH-RLHF**: Human preference dataset
- **Extensible**: Easy to add custom datasets

## 🌐 API Endpoints

### Health
- `GET /api/v1/health/` - Basic health check
- `GET /api/v1/health/detailed` - Detailed component status

### Models
- `GET /api/v1/models/` - List available models
- `GET /api/v1/models/{name}` - Get model information
- `POST /api/v1/models/{name}/test` - Test a model

### Datasets
- `GET /api/v1/datasets/` - List available datasets
- `GET /api/v1/datasets/{name}` - Get dataset information
- `POST /api/v1/datasets/{name}/load` - Load a dataset

### Testing
- `POST /api/v1/testing/run` - Run crash tests
- `GET /api/v1/testing/results/{run_id}` - Get test results
- `GET /api/v1/testing/results` - List test runs

## 💻 CLI Usage

### List Plugins
```bash
python cli.py list
```

### Run Tests
```bash
python cli.py test --model gpt-3.5-turbo --max-tokens 100
```

### Options
- `--model`: Model to test (default: gpt-3.5-turbo)
- `--api-key`: API key (or set OPENAI_API_KEY env var)
- `--max-tokens`: Maximum tokens for responses
- `--temperature`: Model temperature
- `--strict`: Enable strict evaluation mode

## ⚙️ Configuration

Configuration is managed through environment variables or YAML files:

### Environment Variables
```bash
# Application
export APP_NAME="AI Crash Test Prototype"
export DEBUG=false
export LOG_LEVEL=INFO

# API
export API_HOST=0.0.0.0
export API_PORT=8000

# Models
export OPENAI_API_KEY="your_key_here"
export OPENAI_MODEL="gpt-3.5-turbo"
export OPENAI_MAX_TOKENS=200

# Evaluation
export EVALUATOR_NAME="safety"
export EVALUATOR_STRICT=false
```

### YAML Configuration
Create `config.yaml`:
```yaml
app_name: "AI Crash Test Prototype"
version: "2.0.0"
debug: false
log_level: "INFO"

models:
  openai:
    name: "gpt-3.5-turbo"
    provider: "openai"
    api_key: "your_key_here"
    max_tokens: 200
    temperature: 0.7

evaluation:
  evaluator_name: "safety"
  strict_mode: false
```

## 🧪 Adding New Plugins

### New Model Plugin
```python
from src.interfaces.model_interface import ModelInterface
from src.models.config import ModelConfig

class MyModel(ModelInterface):
    def __init__(self, config: ModelConfig):
        super().__init__(config)
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        # Your implementation
        pass
    
    # ... implement other required methods
```

### New Evaluator Plugin
```python
from src.interfaces.evaluator_interface import EvaluatorInterface
from src.models.test_result import TestResult

class MyEvaluator(EvaluatorInterface):
    def evaluate_response(self, prompt, response, expected_behavior):
        # Your evaluation logic
        return TestResult(...)
```

## 📊 Data Models

### Prompt
```python
{
    "id": "uuid",
    "title": "Prompt title",
    "content": "Full prompt text",
    "category": "safety|bias|privacy|general",
    "difficulty": "easy|medium|hard|extreme",
    "expected_behavior": "reject|neutralize|safe_explanation",
    "source": "dataset_name",
    "metadata": {...}
}
```

### Test Result
```python
{
    "id": "test_id",
    "prompt_id": "prompt_id",
    "model_name": "gpt-3.5-turbo",
    "model_response": "Model's response",
    "status": "PASS|FAIL|UNKNOWN|ERROR",
    "category": "safety",
    "difficulty": "hard",
    "expected_behavior": "reject",
    "evaluation_score": 0.85,
    "metadata": {...}
}
```

## 🔧 Development

### Running Tests
```bash
python test_new_architecture.py
```

### Adding Dependencies
Update `requirements.txt` and install:
```bash
pip install -r requirements.txt
```

### Code Style
- Use type hints
- Follow Pydantic models
- Implement interfaces properly
- Add comprehensive docstrings

## 📈 Performance

- **Async Support**: Built-in concurrency for scalable testing
- **Plugin System**: Lazy loading and efficient resource management
- **Configuration**: Environment-based for easy deployment
- **Caching**: Ready for result caching and optimization

## 🛡️ Security

- **API Keys**: Environment variable management
- **Input Validation**: Pydantic model validation
- **Error Handling**: Comprehensive error management
- **Rate Limiting**: Ready for API rate limiting

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For questions and support, please open an issue on GitHub.