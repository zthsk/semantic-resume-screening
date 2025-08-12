# TalentAI MVP: AI-Powered Talent Matching Platform

> **🚀 This is a standalone repository that's part of the [Hack Nation 2025 TalentAI Challenge](https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final)**

## 🎯 Core Value Proposition
Revolutionary AI talent marketplace that matches candidates through **debugging challenges** rather than traditional interviews, with **bias-free evaluation** and **instant job-candidate recommendations**.

## 📋 About This Repository

This repository contains the **core AI modules** extracted from the complete TalentAI platform built during the Hack Nation 2025 hackathon. It focuses on the intelligent components that power the talent matching system:

- **🤖 AI-Powered Resume Parsing & Generation** - Intelligent resume processing with LLM summarization
- **🎯 Semantic Candidate Matching** - Advanced job-candidate compatibility scoring
- **🔍 Skill Extraction & Analysis** - Automated skill identification and assessment

For the **complete full-stack application** including frontend, backend, and full platform features, visit:
**[https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final](https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final)**

## 🚀 Standalone Modules

### 1. Resume Generator & Parser (`resume_generator_parser/`)
**Intelligent resume processing with LLM summarization**

- **Resume Generation**: Creates realistic synthetic resumes in markdown format
- **Resume Parsing**: Extracts structured data (education, experience, skills) from resume files
- **AI Summarization**: Generates professional summaries using Groq API or local LLM models
- **Multiple Output Formats**: JSON, text, and optional PDF generation
- **REST API**: FastAPI-based HTTP interface for backend integration
- **Provider Testing**: Comprehensive testing suite for both Groq and local LLM providers

**Key Features:**
- ✅ Support for both Groq API and local models (Llama, Mistral, Qwen)
- ✅ Automatic provider testing and fallback
- ✅ Command-line interface and REST API
- ✅ Comprehensive error handling and logging
- ✅ Easy integration with existing systems

**Quick Start:**
```bash
cd resume_generator_parser
pip install -r requirements.txt
python main.py --input resume.md --output ./output --provider groq
```

### 2. Candidate Recommendation System (`candidate_recommendation/`)
**AI-powered semantic matching between job descriptions and parsed resumes**

- **Semantic Matching**: Uses Sentence-BERT models for deep semantic understanding
- **Skill-Based Scoring**: Combines semantic similarity with Jaccard skill matching
- **Title Alignment**: Additional scoring based on job title similarity
- **FastAPI Integration**: Modern REST API with automatic documentation
- **Configuration Management**: Environment-based configuration system
- **CLI & API Modes**: Both command-line interface and HTTP API available

**Key Features:**
- ✅ Sentence transformer-based semantic matching
- ✅ Hybrid scoring algorithm (semantic + skills + title)
- ✅ Multiple model support (all-mpnet-base-v2, all-MiniLM-L6-v2, multilingual)
- ✅ Easy integration with resume parser output
- ✅ Comprehensive testing and examples

**Quick Start:**
```bash
cd candidate_recommendation
pip install -r requirements.txt
python main.py --api  # Start API server at http://localhost:8001
```

## 🛠️ Technology Stack

### AI & Machine Learning
- **Sentence Transformers** - Semantic text embeddings for job-candidate matching
- **LangChain** - LLM orchestration and prompt management
- **Groq API** - Fast cloud-based LLM service
- **Local LLMs** - Support for Ollama, LM Studio, and Hugging Face models

### Backend Services
- **FastAPI** - High-performance Python API framework
- **Flask** - Lightweight API framework for candidate recommendation service
- **Pydantic** - Data validation and type safety

### Development & Storage
- **Python 3.8+** - Core development language
- **JSON/Text Files** - Data storage and export formats
- **Environment Variables** - Configuration management

## 🚀 Quick Start

### Prerequisites
```bash
- Python 3.8+
- Groq API key (optional, for cloud LLM)
- Local LLM setup (optional, for offline processing)
```

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd talentai-standalone
   ```

2. **Install dependencies for both modules:**
   ```bash
   # Resume Parser
   cd resume_generator_parser
   pip install -r requirements.txt
   
   # Candidate Recommendation
   cd ../candidate_recommendation
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # For Groq API (optional)
   export GROQ_API_KEY="your-groq-api-key"
   
   # For local LLM (optional)
   export RESUME_PROVIDER="local"
   export RESUME_LOCAL_MODEL_PATH="/path/to/your/model"
   ```

### Running the Modules

**Resume Parser:**
```bash
cd resume_generator_parser

# Process a single resume
python main.py --input resume.md --output ./output --provider groq

# Start REST API
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

**Candidate Recommendation:**
```bash
cd candidate_recommendation

# Start API server
python main.py --api  # Available at http://localhost:8001

# Run CLI demo
python main.py --resumes-dir ../resume_generator_parser/example_output/parsed
```

## 🔄 Integration Workflow

The modules are designed to work together seamlessly:

1. **Resume Processing**: Use `resume_generator_parser` to process resumes and generate structured data
2. **Candidate Matching**: Feed the parsed resume data to `candidate_recommendation` for job matching
3. **API Integration**: Both modules provide REST APIs for easy backend integration

**Example Integration:**
```python
# Process resumes first
from resume_generator_parser.resume_pipeline import CompleteResumePipeline
pipeline = CompleteResumePipeline()
pipeline.run_pipeline(count=5)

# Then match candidates
from candidate_recommendation.semantic_matcher import SemanticMatcher
matcher = SemanticMatcher()
matches = matcher.match_candidates(job, "path/to/parsed/resumes", top_n=5)
```

## 📊 Use Cases

This standalone repository is perfect for:

- **AI Researchers & Developers**: Study semantic matching algorithms and LLM integration
- **Hiring Platform Integrations**: Add intelligent resume processing and candidate matching
- **Resume Processing Systems**: Build automated resume parsing and analysis tools
- **Educational Projects**: Learn about AI-powered hiring and NLP applications
- **Prototyping**: Quick development of talent matching features

## 🌟 Hack Nation 2025

This project was built during the **Hack Nation 2025 TalentAI Challenge** - a hackathon focused on revolutionizing the hiring process through AI-powered talent matching.

**🏆 Complete Application Repository**: [https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final](https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final)

The complete application includes:
- Full-stack frontend applications (React + TypeScript)
- Complete backend services (FastAPI + SQLite)
- Real-time communication and updates
- Comprehensive testing and deployment scripts
- Full platform integration and workflows

## 📚 Documentation

Each module includes comprehensive documentation:

- **`resume_generator_parser/README.md`** - Complete module overview and usage
- **`resume_generator_parser/PIPELINE_README.md`** - End-to-end pipeline guide
- **`resume_generator_parser/SETUP_GUIDE.md`** - LLM setup and configuration
- **`candidate_recommendation/README.md`** - Semantic matching system guide
- **`candidate_recommendation/JOB_MATCHING_GUIDE.md`** - Job-candidate matching guide

## 📄 License

This project is part of the HackNation 2025 TalentAI Challenge.