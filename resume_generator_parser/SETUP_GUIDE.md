# 🚀 Setup Guide for Groq and Local LLM Summarizers

> **🚀 This is a standalone repository that's part of the [Hack Nation 2025 TalentAI Challenge](https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final)**

## 📋 About This Module

This module provides **LLM setup and configuration guidance** extracted from the complete TalentAI platform. It focuses on setting up both cloud-based (Groq) and local LLM providers for resume processing and summarization.

For the **complete full-stack application** including frontend, backend, and full platform features, visit:
**[https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final](https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final)**

## 📋 Prerequisites

### For Groq API:
- Python 3.8+
- Groq API key from [console.groq.com](https://console.groq.com/)

### For Local LLM:
- Python 3.8+
- Sufficient RAM (8GB+ recommended)
- GPU optional but recommended for speed

## 🔧 Installation Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

#### Option A: Using .env file
```bash
# Copy the template
cp env.example .env

# Edit .env file with your settings
nano .env
```

#### Option B: Export directly
```bash
# For Groq
export GROQ_API_KEY="your_actual_groq_api_key"
export RESUME_PROVIDER="groq"

# For Local LLM
export RESUME_PROVIDER="local"
export RESUME_LOCAL_MODEL_PATH="/path/to/your/model"
```

## 🧪 Testing Your Setup

### Quick Test
```bash
python3 test_summarizers.py
```

### Individual Provider Tests

#### Test Groq Only:
```bash
# Set Groq as provider
export RESUME_PROVIDER="groq"
export GROQ_API_KEY="your_key"

# Test
python3 -c "
from llm_summarizer import get_summarizer
s = get_summarizer()
print('Provider:', s.get_current_provider_name())
print('Available:', s.get_available_providers())
"
```

#### Test Local Only:
```bash
# Set Local as provider
export RESUME_PROVIDER="local"

# Test
python3 -c "
from llm_summarizer import get_summarizer
s = get_summarizer()
print('Provider:', s.get_current_provider_name())
print('Available:', s.get_available_providers())
"
```

## 🔍 Troubleshooting

### Groq Issues:
- **"GROQ_API_KEY not set"**: Set your API key in environment
- **"Groq library not installed"**: Run `pip install groq`
- **"Failed to initialize Groq client"**: Check API key validity

### Local LLM Issues:
- **"transformers not installed"**: Run `pip install transformers torch accelerate`
- **"No model path specified"**: Set `RESUME_LOCAL_MODEL_PATH` or use default models
- **"CUDA not available"**: Models will run on CPU (slower but functional)

### Common Issues:
- **Import errors**: Make sure you're in the correct directory
- **Configuration errors**: Check your .env file syntax
- **Permission errors**: Ensure you have read/write access to the directory

## 📊 Expected Test Output

### Successful Groq Test:
```
✅ Groq provider: Available
📝 Test summary: Successfully generated summary
🔧 Provider switching: Working correctly
```

### Successful Local Test:
```
✅ Local provider: Available
📝 Test summary: Successfully generated summary
🔧 Provider switching: Working correctly
```

## 🌟 Hack Nation 2025

This module was built during the **Hack Nation 2025 TalentAI Challenge** - a hackathon focused on revolutionizing the hiring process through AI-powered talent matching.

**🏆 Complete Application Repository**: [https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final](https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final)

This standalone module focuses on **LLM setup and configuration**, making it perfect for:
- AI development environments
- LLM integration projects
- Resume processing systems
- Educational and research purposes
- Multi-provider LLM applications

## License

This project is part of the HackNation 2025 TalentAI Challenge.
