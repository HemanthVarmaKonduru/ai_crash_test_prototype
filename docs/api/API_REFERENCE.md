# 📚 API Reference Documentation

## 🎯 Overview

The AI Security Testing Platform provides a comprehensive REST API for testing AI models against security vulnerabilities. This document provides detailed information about all available endpoints, request/response formats, and usage examples.

---

## 🔗 Base URL

```
Development: http://localhost:8000
Production: https://api.your-domain.com
```

---

## 🔐 Authentication

Currently, the API uses a simplified authentication model. In production, implement proper JWT-based authentication.

### Headers Required
```http
Content-Type: application/json
```

---

## 📊 Health Check

### GET /health

Check the health status of the API server.

**Response:**
```json
{
  "status": "healthy",
  "service": "unified-security-testing"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

## 🎯 Prompt Injection Testing

### POST /api/v1/test/prompt-injection/start

Start a new prompt injection test session.

**Request Body:**
```json
{
  "model_provider": "openai",
  "model_name": "gpt-3.5-turbo",
  "api_endpoint": "https://api.openai.com/v1",
  "api_key": "sk-...",
  "data_type": "prompt_injection",
  "test_mode": "automated"
}
```

**Response:**
```json
{
  "test_id": "pi_1761358997_93a43bdb",
  "status": "initializing",
  "message": "Prompt injection test started successfully",
  "progress": 0,
  "current_step": "Loading prompt injection dataset...",
  "total_tests": 30,
  "completed_tests": 0,
  "results": {}
}
```

**Status Codes:**
- `200 OK` - Test started successfully
- `400 Bad Request` - Invalid request parameters
- `500 Internal Server Error` - Server error

---

### GET /api/v1/test/prompt-injection/{test_id}/status

Get the current status of a prompt injection test.

**Path Parameters:**
- `test_id` (string) - The unique test identifier

**Response:**
```json
{
  "test_id": "pi_1761358997_93a43bdb",
  "status": "running",
  "message": "Processing sample 15/30: pi_015",
  "progress": 50,
  "current_step": "Processing sample 15/30: pi_015",
  "total_tests": 30,
  "completed_tests": 15,
  "results": {
    "successful_captures": 15,
    "failed_captures": 0
  }
}
```

**Status Codes:**
- `200 OK` - Status retrieved successfully
- `404 Not Found` - Test not found

---

### GET /api/v1/test/prompt-injection/{test_id}/results

Get the complete results of a finished prompt injection test.

**Path Parameters:**
- `test_id` (string) - The unique test identifier

**Response:**
```json
{
  "test_id": "pi_1761358997_93a43bdb",
  "status": "completed",
  "start_time": "2024-01-15T10:30:00Z",
  "end_time": "2024-01-15T10:35:00Z",
  "total_tests": 30,
  "completed_tests": 30,
  "detection_rate": 85.5,
  "successful_resistances": 26,
  "failed_resistances": 4,
  "captured_responses": [...],
  "evaluated_responses": [...],
  "detailed_analysis": {
    "technique_distribution": {
      "role_playing": 8,
      "instruction_override": 12,
      "context_manipulation": 10
    },
    "severity_distribution": {
      "low": 15,
      "medium": 10,
      "high": 5
    },
    "language_distribution": {
      "English": 25,
      "Spanish": 3,
      "French": 2
    }
  },
  "performance_metrics": {
    "average_response_time": 1.2,
    "total_api_calls": 60
  }
}
```

**Status Codes:**
- `200 OK` - Results retrieved successfully
- `400 Bad Request` - Test not completed yet
- `404 Not Found` - Test not found

---

### GET /api/v1/test/prompt-injection/{test_id}/download

Download a comprehensive report of the prompt injection test.

**Path Parameters:**
- `test_id` (string) - The unique test identifier

**Response:**
```json
{
  "test_metadata": {
    "test_id": "pi_1761358997_93a43bdb",
    "start_time": "2024-01-15T10:30:00Z",
    "end_time": "2024-01-15T10:35:00Z",
    "total_tests": 30,
    "model_tested": "gpt-3.5-turbo",
    "judge_model": "gpt-4o-mini",
    "api_key_used": "***masked***"
  },
  "summary": {
    "detection_rate": 85.5,
    "successful_resistances": 26,
    "failed_resistances": 4,
    "total_execution_time": 300.5
  },
  "detailed_results": [...],
  "performance_metrics": {...},
  "analysis": {...}
}
```

**Status Codes:**
- `200 OK` - Report generated successfully
- `400 Bad Request` - Test not completed yet
- `404 Not Found` - Test not found

---

## 🔓 Jailbreak Testing

### POST /api/v1/test/jailbreak/start

Start a new jailbreak test session.

**Request Body:**
```json
{
  "model_provider": "openai",
  "model_name": "gpt-3.5-turbo",
  "api_endpoint": "https://api.openai.com/v1",
  "api_key": "sk-...",
  "data_type": "jailbreak",
  "test_mode": "automated"
}
```

**Response:**
```json
{
  "test_id": "jb_1761358991_5a875e9f",
  "status": "initializing",
  "message": "Jailbreak test started successfully",
  "progress": 0,
  "current_step": "Loading jailbreak dataset...",
  "total_tests": 15,
  "completed_tests": 0,
  "results": {}
}
```

**Status Codes:**
- `200 OK` - Test started successfully
- `400 Bad Request` - Invalid request parameters
- `500 Internal Server Error` - Server error

---

### GET /api/v1/test/jailbreak/{test_id}/status

Get the current status of a jailbreak test.

**Path Parameters:**
- `test_id` (string) - The unique test identifier

**Response:**
```json
{
  "test_id": "jb_1761358991_5a875e9f",
  "status": "running",
  "message": "Evaluating jailbreak response 8/15: 7",
  "progress": 75,
  "current_step": "Evaluating jailbreak response 8/15: 7",
  "total_tests": 15,
  "completed_tests": 8,
  "results": {
    "successful_captures": 15,
    "failed_captures": 0,
    "successful_evaluations": 8
  }
}
```

**Status Codes:**
- `200 OK` - Status retrieved successfully
- `404 Not Found` - Test not found

---

### GET /api/v1/test/jailbreak/{test_id}/results

Get the complete results of a finished jailbreak test.

**Path Parameters:**
- `test_id` (string) - The unique test identifier

**Response:**
```json
{
  "test_id": "jb_1761358991_5a875e9f",
  "status": "completed",
  "start_time": "2024-01-15T10:30:00Z",
  "end_time": "2024-01-15T10:33:00Z",
  "total_tests": 15,
  "completed_tests": 15,
  "detection_rate": 73.3,
  "successful_jailbreaks": 4,
  "failed_jailbreaks": 11,
  "captured_responses": [...],
  "evaluated_responses": [...],
  "detailed_analysis": {
    "technique_distribution": {
      "role_playing": 5,
      "developer_mode": 3,
      "academic_context": 4,
      "psychological_experiment": 3
    },
    "risk_category_distribution": {
      "security-violating": 8,
      "harmful-content": 4,
      "privacy-violating": 3
    },
    "language_distribution": {
      "English": 15
    }
  },
  "performance_metrics": {
    "average_response_time": 1.5,
    "total_api_calls": 30
  }
}
```

**Status Codes:**
- `200 OK` - Results retrieved successfully
- `400 Bad Request` - Test not completed yet
- `404 Not Found` - Test not found

---

### GET /api/v1/test/jailbreak/{test_id}/download

Download a comprehensive report of the jailbreak test.

**Path Parameters:**
- `test_id` (string) - The unique test identifier

**Response:**
```json
{
  "test_metadata": {
    "test_id": "jb_1761358991_5a875e9f",
    "start_time": "2024-01-15T10:30:00Z",
    "end_time": "2024-01-15T10:33:00Z",
    "total_tests": 15,
    "model_tested": "gpt-3.5-turbo",
    "judge_model": "gpt-4o-mini",
    "api_key_used": "***masked***"
  },
  "summary": {
    "detection_rate": 73.3,
    "successful_jailbreaks": 4,
    "failed_jailbreaks": 11,
    "total_execution_time": 180.2
  },
  "detailed_results": [...],
  "performance_metrics": {...},
  "analysis": {...}
}
```

**Status Codes:**
- `200 OK` - Report generated successfully
- `400 Bad Request` - Test not completed yet
- `404 Not Found` - Test not found

---

## 📊 Data Models

### TestRequest
```json
{
  "model_provider": "string",
  "model_name": "string",
  "api_endpoint": "string",
  "api_key": "string",
  "data_type": "string",
  "test_mode": "string"
}
```

### TestResponse
```json
{
  "test_id": "string",
  "status": "string",
  "message": "string",
  "progress": "integer",
  "current_step": "string",
  "total_tests": "integer",
  "completed_tests": "integer",
  "results": "object"
}
```

### CapturedResponse
```json
{
  "sample_id": "string",
  "category": "string",
  "technique": "string",
  "severity": "string",
  "language": "string",
  "base_prompt": "string",
  "injection_prompt": "string",
  "model_response": "string",
  "response_time": "number",
  "api_model": "string",
  "capture_success": "boolean"
}
```

### EvaluatedResponse
```json
{
  "sample_id": "string",
  "category": "string",
  "technique": "string",
  "severity": "string",
  "language": "string",
  "injection_prompt": "string",
  "model_response": "string",
  "injection_successful": "boolean",
  "confidence_score": "number",
  "safety_score": "number",
  "reasoning": "string",
  "evaluation": "object",
  "metadata": "object"
}
```

---

## 🔄 Status Values

### Test Status
- `initializing` - Test is being set up
- `running` - Test is in progress
- `completed` - Test finished successfully
- `failed` - Test encountered an error

### Progress Values
- `0-100` - Percentage completion of the test

---

## ⚠️ Error Handling

### Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Codes
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

---

## 🚀 Usage Examples

### JavaScript/TypeScript
```javascript
// Start a prompt injection test
const response = await fetch('http://localhost:8000/api/v1/test/prompt-injection/start', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    model_provider: 'openai',
    model_name: 'gpt-3.5-turbo',
    api_endpoint: 'https://api.openai.com/v1',
    api_key: 'sk-...',
    data_type: 'prompt_injection',
    test_mode: 'automated'
  })
});

const data = await response.json();
console.log('Test ID:', data.test_id);

// Poll for status updates
const pollStatus = async (testId) => {
  const statusResponse = await fetch(`http://localhost:8000/api/v1/test/prompt-injection/${testId}/status`);
  const statusData = await statusResponse.json();
  
  console.log(`Progress: ${statusData.progress}% - ${statusData.current_step}`);
  
  if (statusData.status === 'completed') {
    // Get final results
    const resultsResponse = await fetch(`http://localhost:8000/api/v1/test/prompt-injection/${testId}/results`);
    const results = await resultsResponse.json();
    console.log('Final Results:', results);
  } else if (statusData.status === 'running') {
    // Continue polling
    setTimeout(() => pollStatus(testId), 2000);
  }
};

pollStatus(data.test_id);
```

### Python
```python
import requests
import time

# Start a jailbreak test
response = requests.post('http://localhost:8000/api/v1/test/jailbreak/start', json={
    'model_provider': 'openai',
    'model_name': 'gpt-3.5-turbo',
    'api_endpoint': 'https://api.openai.com/v1',
    'api_key': 'sk-...',
    'data_type': 'jailbreak',
    'test_mode': 'automated'
})

test_data = response.json()
test_id = test_data['test_id']
print(f'Test ID: {test_id}')

# Poll for status updates
while True:
    status_response = requests.get(f'http://localhost:8000/api/v1/test/jailbreak/{test_id}/status')
    status_data = status_response.json()
    
    print(f'Progress: {status_data["progress"]}% - {status_data["current_step"]}')
    
    if status_data['status'] == 'completed':
        # Get final results
        results_response = requests.get(f'http://localhost:8000/api/v1/test/jailbreak/{test_id}/results')
        results = results_response.json()
        print('Final Results:', results)
        break
    elif status_data['status'] == 'failed':
        print('Test failed')
        break
    
    time.sleep(2)
```

### cURL
```bash
# Start a prompt injection test
curl -X POST http://localhost:8000/api/v1/test/prompt-injection/start \
  -H "Content-Type: application/json" \
  -d '{
    "model_provider": "openai",
    "model_name": "gpt-3.5-turbo",
    "api_endpoint": "https://api.openai.com/v1",
    "api_key": "sk-...",
    "data_type": "prompt_injection",
    "test_mode": "automated"
  }'

# Check status
curl -X GET http://localhost:8000/api/v1/test/prompt-injection/{test_id}/status

# Get results
curl -X GET http://localhost:8000/api/v1/test/prompt-injection/{test_id}/results

# Download report
curl -X GET http://localhost:8000/api/v1/test/prompt-injection/{test_id}/download
```

---

## 📈 Rate Limits

Currently, there are no rate limits implemented. In production, consider implementing:
- 10 requests per minute per IP
- 100 requests per hour per API key
- 5 concurrent tests per user

---

## 🔧 SDKs and Libraries

### Official SDKs
- **JavaScript/TypeScript**: Available via npm
- **Python**: Available via pip
- **Go**: Available via go modules

### Community Libraries
- **Java**: Spring Boot integration
- **C#**: .NET Core integration
- **Ruby**: Ruby gem available

---

This API reference provides comprehensive documentation for all endpoints, data models, and usage examples for the AI Security Testing Platform.
