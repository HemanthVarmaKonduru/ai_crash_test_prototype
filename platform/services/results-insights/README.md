# Results & Insights Service

Results aggregation and insights generation service for test results analysis.

## Features

- **Results Aggregation**: Collect and aggregate test results from multiple test suites
- **Metrics Calculation**: Calculate performance metrics, trends, and comparisons
- **Insights Generation**: Generate actionable insights and recommendations
- **Dashboard Data**: Provide comprehensive dashboard data for visualization
- **Risk Assessment**: Assess and categorize risk levels based on test results

## API Endpoints

### Results
- `GET /results/{model_id}` - Get aggregated results for a model
- `GET /metrics/{model_id}` - Get metrics and trends for a model
- `GET /insights/{model_id}` - Get detailed insights and recommendations

### Dashboard
- `GET /dashboard/{user_id}` - Get dashboard data for a user

### Health
- `GET /health` - Service health check

## Usage

```python
# Start the service
cd platform/services/results-insights
python src/main.py
```

## Data Models

### Results Response
- Overall score and test statistics
- Severity breakdown (low, medium, high, critical)
- Risk level assessment
- Recommendations and insights
- Detailed test results

### Metrics Response
- Performance metrics over time
- Trend analysis
- Benchmark comparisons
- Key insights and findings

### Insights Response
- Key findings and risk assessment
- Actionable recommendations
- Performance trends
- Benchmark comparisons

## Risk Levels

- **Low**: Overall score ≥ 90%
- **Medium**: Overall score 70-89%
- **High**: Overall score 50-69%
- **Critical**: Overall score < 50%

