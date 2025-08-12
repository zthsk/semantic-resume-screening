# Resume Parser with LLM Summarization

> **🚀 This is a standalone repository that's part of the [Hack Nation 2025 TalentAI Challenge](https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final)**

A Python-based resume parsing and summarization system that supports both Groq API and local LLM models. The system automatically tests both providers and allows easy switching between them.

## 📋 About This Module

This module provides **intelligent resume processing** capabilities extracted from the complete TalentAI platform. It focuses on automated resume parsing, skill extraction, and AI-powered summarization for hiring decisions.

For the **complete full-stack application** including frontend, backend, and full platform features, visit:
**[https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final](https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final)**

## Features

- **Resume Parsing**: Parse markdown and text resume files into structured data
- **LLM Summarization**: Generate professional summaries using:
  - **Groq API**: Fast, reliable cloud-based LLM service
  - **Local Models**: Run open-source models locally (e.g., Llama, Mistral, Qwen)
- **Provider Testing**: Comprehensive testing suite for both providers
- **Multiple Output Formats**: JSON, text, and optional PDF generation
- **REST API**: FastAPI-based HTTP interface for backend integration
- **Command Line Interface**: Process files and directories from CLI

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd hackathon
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # Create .env file
   cp env.example .env
   
   # Edit .env with your settings
   echo "GROQ_API_KEY=your_groq_api_key_here" >> .env
   echo "RESUME_PROVIDER=groq" >> .env
   ```

## Configuration

### Environment Variables

- `GROQ_API_KEY`: Your Groq API key (required for Groq provider)
- `RESUME_PROVIDER`: LLM provider to use (`groq` or `local`)
- `RESUME_GROQ_MODEL`: Groq model name (default: `llama3-8b-8192`)
- `RESUME_LOCAL_MODEL_PATH`: Path to local model (for local provider)
- `RESUME_LOCAL_DEVICE`: Device for local models (`gpu` or `cpu`)

### Local Model Setup

To use local models, install additional dependencies:
```bash
pip install transformers torch accelerate sentencepiece
```

Then set the model path in your `.env`:
```bash
RESUME_PROVIDER=local
RESUME_LOCAL_MODEL_PATH=/path/to/your/model
RESUME_LOCAL_DEVICE=gpu  # or cpu
```

## Testing

The system includes comprehensive testing for both LLM providers:

### Run All Tests
```bash
python test_summarizers.py
```

This will test:
- Configuration loading
- Individual provider availability
- Provider switching functionality
- Both providers side by side
- Actual summarization with each provider

### Test Specific Components
```bash
# Test basic system functionality
python test_system.py

# Test simple imports
python simple_test.py
```

### Test Results
The test suite provides detailed feedback on:
- ✅ Provider availability and status
- 🔄 Provider switching success
- 📝 Summarization quality and performance
- 📊 Comparison between providers

## Usage

### Command Line Interface

**Process a single resume file:**
```bash
python main.py --input resume.md --output ./output --provider groq
```

**Process multiple resumes:**
```bash
python main.py --input ./resumes/ --output ./output/ --provider groq --pattern "*.md"
```

**Generate synthetic resumes:**
```bash
python main.py --output ./synthetic --generate 10 --make-pdf
```

### REST API

**Start the API server:**
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

**API Endpoints:**
- `GET /`: API information
- `GET /health`: Health check
- `GET /providers`: Available LLM providers and their status
- `POST /parse`: Parse resume from text content
- `POST /parse-file`: Parse resume from uploaded file
- `POST /parse-batch`: Parse multiple resume files
- `POST /generate`: Generate synthetic resumes
- `POST /set-provider`: Set LLM provider dynamically

**Example API usage:**
```bash
# Parse a resume file
curl -X POST "http://localhost:8000/parse-file" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume.md" \
  -F "provider=groq" \
  -F "max_length=200"

# Check available providers
curl "http://localhost:8000/providers"

# Switch providers
curl -X POST "http://localhost:8000/set-provider" \
  -H "Content-Type: application/json" \
  -d '"local"'
```

## Resume Format

The system expects resumes in a specific markdown format:

```markdown
# John Doe
## Software Engineer

Email: john.doe@email.com
Phone: (555) 123-4567
Location: San Francisco, CA

### Education
- Bachelor of Science in Computer Science from Stanford University (2020)

### Experience
- Senior Software Engineer at TechCorp (Jan 2021 - Present)
  * Led development of microservices architecture
  * Improved system performance by 40%

### Skills
#### Programming: Python, JavaScript, Go
#### Web: React, Node.js, FastAPI
#### Cloud: AWS, Docker, Kubernetes
```

## Supported LLM Providers

### Groq API
- **Models**: llama3-8b-8192, mixtral-8x7b-32768, gemma2-9b-it
- **Features**: Fast inference, reliable API, cost-effective
- **Setup**: Requires Groq API key
- **Best for**: Production use, high throughput, cost optimization

### Local Models
- **Models**: Any Hugging Face transformers model (Llama, Mistral, Qwen, etc.)
- **Features**: Privacy, no API costs, customizable, offline operation
- **Setup**: Requires local model files and sufficient compute
- **Best for**: Privacy-sensitive environments, cost control, customization

## Provider Testing and Comparison

The system automatically tests both providers and provides detailed feedback:

### Automatic Provider Selection
- System automatically selects the best available provider
- Falls back gracefully if preferred provider is unavailable
- Provides clear status information for each provider

### Provider Switching
- Switch between providers at runtime
- Test both providers with the same resume
- Compare output quality and performance

### Testing Output Example
```
🔄 Testing Both Providers Side by Side...
   Available providers: {'groq': True, 'local': False}
   🔄 Testing groq provider...
   ✅ groq: Success!
      📊 Length: 156 chars
      📝 Preview: John Doe is a Software Engineer with expertise in Python...

📊 Provider Test Results:
      ✅ groq: success
      ⏭️ local: not_available
```

## Error Handling

The system includes comprehensive error handling:
- Graceful fallback to basic summaries if LLM fails
- Detailed logging for debugging
- Input validation and sanitization
- File format detection and support
- Provider availability checking

## Development

### Project Structure
```
├── api.py                 # FastAPI REST interface
├── config.py              # Configuration management
├── generator_parser.py    # Synthetic resume generator
├── llm_summarizer.py      # LLM integration layer (Groq + Local)
├── main.py                # Command line interface
├── models.py              # Data models and structures
├── resume_generator.py    # Resume generation utilities
├── resume_parser.py       # Resume parsing logic
├── test_summarizers.py    # Comprehensive provider testing
├── test_system.py         # System integration testing
├── simple_test.py         # Basic import testing
└── requirements.txt       # Python dependencies
```

### Adding New LLM Providers

To add a new LLM provider:

1. Create a new provider class inheriting from `LLMProvider`
2. Implement the required methods: `summarize()` and `is_available()`
3. Add the provider to the `LLMSummarizer.providers` dictionary
4. Update configuration as needed
5. Add tests to `test_summarizers.py`

### Testing New Providers

The testing framework automatically detects and tests new providers:
```python
# Add your provider
self.providers = {
    "groq": GroqProvider(),
    "local": LocalProvider(),
    "your_provider": YourProvider()  # New provider
}
```

## Troubleshooting

### Common Issues

1. **Groq API errors**: Verify your API key and model name
2. **Local model loading**: Ensure sufficient RAM/VRAM and correct model path
3. **Parsing errors**: Check resume format matches expected structure
4. **Import errors**: Install missing dependencies from requirements.txt
5. **Provider not available**: Check configuration and dependencies

### Provider-Specific Issues

**Groq Provider:**
- Verify `GROQ_API_KEY` is set correctly
- Check model name is valid
- Ensure internet connectivity

**Local Provider:**
- Install required packages: `pip install transformers torch accelerate sentencepiece`
- Verify model path is correct
- Check available memory (models can require 4-16GB+ RAM/VRAM)

### Logging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🌟 Hack Nation 2025

This module was built during the **Hack Nation 2025 TalentAI Challenge** - a hackathon focused on revolutionizing the hiring process through AI-powered talent matching.

**🏆 Complete Application Repository**: [https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final](https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final)

This standalone module focuses on **resume processing and AI summarization**, making it perfect for:
- Resume parsing systems
- AI-powered hiring tools
- Document processing applications
- LLM integration projects
- Educational and research purposes

## License

This project is part of the HackNation 2025 TalentAI Challenge.
## Contributing

This project is part of the HackNation 2025 TalentAI Challenge.

