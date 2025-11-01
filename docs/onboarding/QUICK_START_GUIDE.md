# 🚀 Quick Start Guide - AI Security Testing Platform

## 🎯 Welcome!

This guide will get you up and running with the AI Security Testing Platform in under 10 minutes. You'll be able to test AI models against prompt injection and jailbreak attacks with real-time monitoring and comprehensive reporting.

---

## ⚡ 5-Minute Setup

### Prerequisites
- Python 3.12+
- Node.js 18+
- OpenAI API Key

### Step 1: Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd ai_crash_test_prototype

# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
```

### Step 2: Start Backend
```bash
# Start the API server
python backend/run.py
```
✅ **Backend running on http://localhost:8000**

### Step 3: Start Frontend
```bash
# In a new terminal, start the frontend
cd frontend
npm install
npm run dev
```
✅ **Frontend running on http://localhost:3000**

### Step 4: Test the System
```bash
# Test API health
curl http://localhost:8000/health

# Open the dashboard
open http://localhost:3000/dashboard
```

---

## 🎮 Your First Test

### Prompt Injection Test

1. **Navigate to Prompt Injection Module**
   - Go to `http://localhost:3000/dashboard/prompt-injection`

2. **Configure Test Parameters**
   - Model Provider: `OpenAI`
   - Model Name: `GPT-3.5 Turbo`
   - API Key: `your-api-key` (will be overridden by backend)
   - Test Mode: `Automated`

3. **Start the Test**
   - Click "Execute Prompt Injection Test"
   - Watch real-time progress updates
   - See live status: "Loading dataset...", "Capturing responses...", "Evaluating..."

4. **View Results**
   - Total Tests: 30
   - Successful Resistances: Model defended against attacks
   - Failed Resistances: Model was compromised
   - Detection Rate: Overall security score

5. **Explore Details**
   - Click on "Failed Resistances" to see compromised responses
   - Click on "Successful Resistances" to see defended responses
   - Download comprehensive report

### Jailbreak Test

1. **Navigate to Jailbreak Module**
   - Go to `http://localhost:3000/dashboard/jailbreak`

2. **Run Jailbreak Test**
   - Same configuration as prompt injection
   - Click "Execute Jailbreak Test"
   - Monitor 15 sophisticated jailbreak attempts

3. **Analyze Results**
   - Successful Jailbreaks: Model bypassed safety guidelines
   - Failed Jailbreaks: Model maintained safety
   - Detection Rate: Security effectiveness

---

## 📊 Understanding the Results

### Key Metrics Explained

| Metric | Description | Good Score |
|--------|-------------|------------|
| **Detection Rate** | % of attacks successfully defended | >80% |
| **Successful Resistances** | Number of defended attacks | Higher is better |
| **Failed Resistances** | Number of successful attacks | Lower is better |
| **Response Time** | Average API response time | <2 seconds |

### Result Categories

#### 🟢 **Successful Resistances (Good)**
- Model refused to comply with malicious requests
- Maintained safety guidelines
- Provided appropriate responses

#### 🔴 **Failed Resistances (Concerning)**
- Model complied with malicious requests
- Bypassed safety guidelines
- Potential security vulnerability

### Detailed Analysis

Each result includes:
- **Original Prompt**: The attack attempt
- **Model Response**: How the model responded
- **AI Evaluation**: GPT-4o-mini's assessment
- **Confidence Score**: How certain the evaluation is
- **Reasoning**: Why the evaluation was made

---

## 🔍 Exploring the Interface

### Dashboard Overview
- **Test History**: View all previous test runs
- **Real-time Progress**: Live updates during testing
- **Interactive Results**: Clickable cards for detailed views
- **Export Options**: Download reports in JSON format

### Navigation
- **Dashboard**: Main overview page
- **Prompt Injection**: Test against prompt injection attacks
- **Jailbreak**: Test against jailbreak attempts
- **Reports**: Historical analysis and trends

### Features
- **Search**: Filter test history by ID, model, or type
- **Persistence**: Test history saved across browser sessions
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: No page refresh needed

---

## 🛠️ Advanced Usage

### Custom Configuration

#### Environment Variables
```bash
# Set custom API key
export OPENAI_API_KEY="sk-your-key-here"

# Set custom model (optional)
export TARGET_MODEL="gpt-4"
export JUDGE_MODEL="gpt-4o-mini"

# Set test limits
export MAX_PROMPTS_PI=50  # More prompt injection tests
export MAX_PROMPTS_JB=25  # More jailbreak tests
```

#### API Usage
```bash
# Start a test programmatically
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
curl http://localhost:8000/api/v1/test/prompt-injection/{test_id}/status

# Get results
curl http://localhost:8000/api/v1/test/prompt-injection/{test_id}/results
```

### Batch Testing

#### Multiple Models
```python
import requests
import time

models = ["gpt-3.5-turbo", "gpt-4", "gpt-4o-mini"]
results = {}

for model in models:
    # Start test
    response = requests.post('http://localhost:8000/api/v1/test/prompt-injection/start', json={
        'model_provider': 'openai',
        'model_name': model,
        'api_endpoint': 'https://api.openai.com/v1',
        'api_key': 'sk-...',
        'data_type': 'prompt_injection',
        'test_mode': 'automated'
    })
    
    test_id = response.json()['test_id']
    
    # Wait for completion
    while True:
        status = requests.get(f'http://localhost:8000/api/v1/test/prompt-injection/{test_id}/status')
        if status.json()['status'] == 'completed':
            break
        time.sleep(5)
    
    # Get results
    results[model] = requests.get(f'http://localhost:8000/api/v1/test/prompt-injection/{test_id}/results').json()

# Compare results
for model, result in results.items():
    print(f"{model}: {result['detection_rate']:.1f}% detection rate")
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. API Server Won't Start
```bash
# Check if port 8000 is available
netstat -tulpn | grep :8000

# Check Python dependencies
pip install fastapi uvicorn openai

# Check API key
echo $OPENAI_API_KEY
```

#### 2. Frontend Won't Load
```bash
# Check Node.js version
node --version  # Should be 18+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check if port 3000 is available
netstat -tulpn | grep :3000
```

#### 3. Tests Failing
```bash
# Check API key validity
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

# Check network connectivity
curl https://api.openai.com/v1/models

# Check server logs
python backend/run.py  # Look for error messages
```

#### 4. Slow Performance
```bash
# Check system resources
top
htop

# Reduce test sample size
export MAX_PROMPTS_PI=10
export MAX_PROMPTS_JB=5

# Check network latency
ping api.openai.com
```

### Getting Help

#### Logs and Debugging
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python backend/run.py

# Check browser console
# Open Developer Tools (F12) and check Console tab

# Check network requests
# Open Developer Tools (F12) and check Network tab
```

#### Support Resources
- **Documentation**: Check `/docs` directory
- **API Docs**: Visit `http://localhost:8000/docs`
- **GitHub Issues**: Report bugs and feature requests
- **Community**: Join our Discord/Slack

---

## 📈 Next Steps

### 1. Explore Advanced Features
- **Custom Datasets**: Add your own test prompts
- **Batch Testing**: Test multiple models simultaneously
- **API Integration**: Integrate with your existing systems
- **Automated Testing**: Set up CI/CD pipelines

### 2. Production Deployment
- **Docker**: Containerize your deployment
- **Kubernetes**: Scale with container orchestration
- **Monitoring**: Set up alerts and dashboards
- **Security**: Implement proper authentication

### 3. Customization
- **UI Themes**: Customize the interface
- **Test Types**: Add new attack vectors
- **Evaluation Logic**: Customize AI evaluation
- **Reporting**: Create custom report formats

### 4. Integration
- **CI/CD**: Automated security testing
- **APIs**: RESTful API for external systems
- **Webhooks**: Real-time notifications
- **Analytics**: Advanced metrics and insights

---

## 🎯 Success Metrics

### What Good Results Look Like

#### Excellent Security (90%+ Detection Rate)
- Model consistently refuses malicious requests
- Provides helpful alternatives
- Maintains safety guidelines

#### Good Security (80-90% Detection Rate)
- Most attacks are defended
- Some edge cases may succeed
- Generally safe for production

#### Needs Improvement (<80% Detection Rate)
- Multiple successful attacks
- Safety guidelines frequently bypassed
- Requires immediate attention

### Benchmarking

#### Industry Standards
- **GPT-4**: Typically 85-95% detection rate
- **GPT-3.5**: Typically 70-85% detection rate
- **Claude**: Typically 80-90% detection rate

#### Your Baseline
- Run tests regularly to establish baseline
- Track improvements over time
- Compare different model versions

---

## 🎉 Congratulations!

You've successfully set up and run your first AI security tests! The platform is now ready for:

- **Regular Security Audits**: Test your models regularly
- **Model Comparison**: Compare different AI models
- **Security Monitoring**: Track security trends over time
- **Compliance Reporting**: Generate reports for stakeholders

### Quick Commands Reference

```bash
# Start everything
python backend/run.py &
cd frontend && npm run dev

# Test API
curl http://localhost:8000/health

# Stop everything
pkill -f "python backend/run.py"
pkill -f "npm run dev"
```

### Useful URLs
- **Dashboard**: http://localhost:3000/dashboard
- **Prompt Injection**: http://localhost:3000/dashboard/prompt-injection
- **Jailbreak**: http://localhost:3000/dashboard/jailbreak
- **API Health**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs

---

**Happy Testing! 🚀**

For more advanced usage, check out the [Deployment Guide](../runbooks/DEPLOYMENT_GUIDE.md) and [API Reference](../api/API_REFERENCE.md).
