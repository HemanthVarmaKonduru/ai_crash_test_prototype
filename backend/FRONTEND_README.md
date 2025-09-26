# AI Crash Test Prototype - Streamlit Frontend

## Overview

This Streamlit frontend provides an interactive web interface for testing AI models with safety prompts. Users can input their API key, select the number of prompts to test, and view detailed results.

## Features

- 🔐 **Secure API Key Input**: Password-protected input for OpenAI API keys
- 🎯 **Model Selection**: Choose from different OpenAI models (GPT-3.5, GPT-4, etc.)
- 📊 **Configurable Testing**: Select how many prompts to test (1-100)
- 📈 **Real-time Progress**: Live progress bar and status updates during testing
- 📋 **Detailed Results**: Comprehensive analysis of test results
- 📊 **Category Breakdown**: Results organized by prompt categories
- 🎨 **Modern UI**: Clean, responsive interface with metrics and visualizations

## How to Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Streamlit App**:
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Access the Interface**:
   - Open your browser to `http://localhost:8501`
   - The app will automatically open in your default browser

## Usage

### 1. Configuration (Sidebar)
- **API Key**: Enter your OpenAI API key (password-protected)
- **Model**: Select the AI model to test
- **Number of Prompts**: Choose how many prompts to test (1-100)

### 2. Running Tests
- Click "🚀 Run Crash Tests" to start testing
- Watch the progress bar and status updates
- Results will appear automatically when complete

### 3. Viewing Results
- **Summary Metrics**: Total tests, pass/fail rates
- **Category Breakdown**: Results by prompt category
- **Detailed Results**: Expandable sections for each test
- **Model Responses**: Full text of AI model responses

## Dataset Information

The app uses the `crash_test_prompts.jsonl` file which contains:
- Safety prompts
- Bias detection prompts  
- Privacy-related prompts
- General conversation prompts

Each prompt includes:
- Category classification
- Difficulty level
- Expected behavior
- Metadata

## Technical Details

### Architecture
- Built with Streamlit for rapid web app development
- Integrates with the modular backend architecture
- Uses async/await for efficient API calls
- Real-time progress tracking

### Components
- **Prompt Loading**: Loads prompts from JSONL file
- **Model Integration**: Connects to OpenAI API
- **Evaluation Engine**: Uses safety evaluator for response analysis
- **Results Display**: Interactive results visualization

### Error Handling
- Graceful handling of API errors
- File not found protection
- Invalid prompt handling
- Network timeout management

## Customization

### Adding New Models
1. Implement the `ModelInterface` in `src/interfaces/`
2. Register the model in the plugin system
3. Add to the model selection dropdown

### Adding New Evaluators
1. Implement the `EvaluatorInterface` in `src/interfaces/`
2. Register the evaluator in the plugin system
3. The app will automatically use the new evaluator

### Modifying the UI
- Edit `streamlit_app.py` to customize the interface
- Add new metrics or visualizations
- Modify the layout and styling

## Troubleshooting

### Common Issues

1. **Import Errors**:
   - Ensure you're running from the backend directory
   - Check that all dependencies are installed

2. **API Key Issues**:
   - Verify your OpenAI API key is valid
   - Check that you have sufficient API credits

3. **File Not Found**:
   - Ensure `crash_test_prompts.jsonl` exists in the backend directory
   - Check file permissions

4. **Port Conflicts**:
   - Use `--server.port 8502` to run on a different port
   - Kill existing Streamlit processes if needed

### Performance Tips

- Start with fewer prompts (5-10) for initial testing
- Use GPT-3.5-turbo for faster, cheaper testing
- Monitor API usage and costs
- Consider rate limiting for large test batches

## Security Notes

- API keys are handled securely (password input)
- No API keys are stored or logged
- All data processing happens locally
- Results are not persisted unless explicitly saved

## Future Enhancements

- [ ] Export results to CSV/JSON
- [ ] Batch testing with multiple models
- [ ] Custom prompt input
- [ ] Advanced filtering and search
- [ ] Historical test comparison
- [ ] Real-time model monitoring
- [ ] Integration with other AI providers


