# Complete Resume Pipeline

> **🚀 This is a standalone repository that's part of the [Hack Nation 2025 TalentAI Challenge](https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final)**

This project provides a comprehensive pipeline for generating synthetic resumes, parsing them to extract structured information, generating AI-powered summaries using Groq, and saving all data to organized JSON files.

## 📋 About This Module

This module provides **comprehensive resume processing capabilities** extracted from the complete TalentAI platform. It focuses on end-to-end resume generation, parsing, and AI-powered summarization for hiring decisions.

For the **complete full-stack application** including frontend, backend, and full platform features, visit:
**[https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final](https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final)**

## Features

- **Resume Generation**: Creates realistic synthetic resumes in markdown format
- **Resume Parsing**: Extracts structured data (education, experience, skills) from resume files
- **AI Summarization**: Generates professional summaries using Groq's LLM service
- **Data Export**: Saves parsed data and summaries to organized JSON and text files
- **Pipeline Reporting**: Comprehensive execution reports and statistics

## Prerequisites

- Python 3.8+
- Groq API key (for LLM summarization)
- Required Python packages (see `requirements.txt`)

## Installation

1. **Clone or download the project files**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set your Groq API key:**
   ```bash
   export GROQ_API_KEY="your-api-key-here"
   ```
   
   Or create a `.env` file:
   ```bash
   echo "GROQ_API_KEY=your-api-key-here" > .env
   ```

## Usage

### Command Line Interface

The main script can be run from the command line:

```bash
# Generate 5 resumes (default)
python resume_pipeline_complete.py

# Generate 10 resumes
python resume_pipeline_complete.py --count 10

# Specify output directory
python resume_pipeline_complete.py --output-dir ./my_resumes

# Provide Groq API key directly
python resume_pipeline_complete.py --groq-api-key "your-key-here"

# Enable verbose logging
python resume_pipeline_complete.py --verbose
```

### Programmatic Usage

You can also use the pipeline in your own Python code:

```python
from resume_pipeline_complete import CompleteResumePipeline
from pathlib import Path

# Initialize pipeline
pipeline = CompleteResumePipeline(
    output_dir=Path("./output"),
    groq_api_key="your-api-key"
)

# Run pipeline
results = pipeline.run_pipeline(count=5)

if results["success"]:
    print(f"Generated {results['statistics']['successfully_generated']} resumes")
    print(f"Execution time: {results['statistics']['execution_time_seconds']} seconds")
```

See `example_usage.py` for a complete example.

## Output Structure

The pipeline creates the following directory structure:

```
output_directory/
├── resumes/                    # Generated markdown resume files
│   ├── alex_johnson_001.md
│   ├── jordan_smith_002.md
│   └── ...
├── parsed/                     # JSON files with parsed data + summaries
│   ├── alex_johnson_001_parsed.json
│   ├── jordan_smith_002_parsed.json
│   └── ...
├── summaries/                  # Text files with just the summaries
│   ├── alex_johnson_001_summary.txt
│   ├── jordan_smith_002_summary.txt
│   └── ...
└── combined.json               # Combined data from all resumes
```

## 🌟 Hack Nation 2025

This module was built during the **Hack Nation 2025 TalentAI Challenge** - a hackathon focused on revolutionizing the hiring process through AI-powered talent matching.

**🏆 Complete Application Repository**: [https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final](https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final)

This standalone module focuses on **resume pipeline processing**, making it perfect for:
- Resume generation systems
- Document processing pipelines
- AI-powered hiring tools
- Data generation and testing
- Educational and research purposes

## License

This project is part of the HackNation 2025 TalentAI Challenge.
