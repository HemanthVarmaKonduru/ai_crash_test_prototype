# Job Executor Service

Job execution service for test suite processing with real-time WebSocket updates.

## Features

- **Test Job Execution**: Execute safety, bias, robustness, and adversarial test suites
- **Real-time Updates**: WebSocket-based progress tracking and status updates
- **Job Management**: Create, monitor, and cancel test jobs
- **Results Processing**: Generate structured test results and metrics
- **Event Publishing**: Real-time event notifications for frontend integration

## API Endpoints

### Job Management
- `POST /jobs` - Create a new test job
- `GET /jobs/{job_id}` - Get job status and results
- `GET /jobs` - List jobs for a user
- `DELETE /jobs/{job_id}` - Cancel a job

### WebSocket
- `WS /ws/{user_id}` - Real-time job updates

### Health
- `GET /health` - Service health check

## Usage

```python
# Start the service
cd platform/services/job-executor
python src/main.py
```

## Test Suites

- **Safety**: 5 tests for content safety and harm detection
- **Bias**: 4 tests for bias detection and fairness
- **Robustness**: 6 tests for model robustness and reliability
- **Adversarial**: 8 tests for adversarial attack resistance

## WebSocket Events

The service publishes real-time events for:
- Job creation and status updates
- Progress tracking during execution
- Completion notifications with results
- Error handling and failure notifications

