# Prompt Injection Testing Service

## Overview

The Prompt Injection Testing Service is a specialized microservice that performs real-time testing of AI models against prompt injection attacks. It integrates with the existing platform to provide comprehensive security testing capabilities.

## Features

- **Real-time Testing**: Live testing using OpenAI API
- **Comprehensive Dataset**: 167+ prompt injection samples
- **Multi-language Support**: Testing across 17 languages
- **Severity-based Testing**: Critical to low severity stratification
- **Background Processing**: Asynchronous test execution
- **Event Publishing**: Real-time updates via WebSocket
- **Detailed Analytics**: Comprehensive test results and metrics

## API Endpoints

### Health Check
```
GET /health
```

### Start Testing
```
POST /test/start
{
    "dataset_path": "prompt_injection_comprehensive_processed.json",
    "batch_size": 10,
    "model": "gpt-3.5-turbo",
    "max_tokens": 150,
    "temperature": 0.7
}
```

### Get Test Status
```
GET /test/status/{session_id}
```

### Get Test Results
```
GET /test/results/{session_id}
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API key for testing
- `PORT`: Service port (default: 8002)

### Dependencies
- FastAPI for API framework
- OpenAI for model testing
- Pydantic for data validation
- AsyncIO for concurrent processing

## Usage

### Start the Service
```bash
cd platform/services/prompt-injection-tester
python src/main.py
```

### Test with Quick Script
```bash
cd data
python quick_test.py
```

### Integration with Platform
The service integrates with:
- **API Gateway**: Model connection management
- **Job Executor**: Test execution orchestration
- **Results & Insights**: Analytics and reporting
- **Event System**: Real-time updates

## Testing Framework

### Test Categories
- **Direct Injection**: Explicit instruction override attempts
- **Indirect Injection**: Subtle manipulation techniques
- **Role Playing**: Identity confusion attacks
- **Social Engineering**: Psychological manipulation
- **Technical Exploitation**: System access attempts
- **Context Manipulation**: Interpretation context changes
- **Multilingual Attacks**: Cross-language injection attempts

### Success Metrics
- **Injection Prevention Rate**: >95% target
- **False Positive Rate**: <5% target
- **Multilingual Consistency**: <10% variance
- **Recovery Time**: <2 seconds
- **Context Awareness**: >90% accuracy

## Development

### Install Dependencies
```bash
pip install -e .
```

### Run Tests
```bash
pytest tests/
```

### Code Quality
```bash
black src/
flake8 src/
mypy src/
```

## Integration

This service is designed to work seamlessly with the existing platform architecture:

1. **API Gateway** handles model connections
2. **Job Executor** orchestrates test execution
3. **Results & Insights** processes analytics
4. **Event System** provides real-time updates
5. **Frontend Dashboard** displays results

## Security Considerations

- API keys are securely managed
- Test data is processed in memory
- Results are stored temporarily
- No sensitive data persistence
- Rate limiting to prevent abuse

## Performance

- **Concurrent Testing**: Batch processing for efficiency
- **Rate Limiting**: Respects API limits
- **Memory Management**: Efficient data handling
- **Error Handling**: Robust error recovery
- **Monitoring**: Comprehensive logging

## Future Enhancements

- Support for additional models
- Custom dataset upload
- Advanced analytics
- Machine learning insights
- Automated reporting
- Integration with CI/CD

