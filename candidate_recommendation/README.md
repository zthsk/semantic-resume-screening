# Candidate Recommendation System

> **🚀 This is a standalone repository that's part of the [Hack Nation 2025 TalentAI Challenge](https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final)**

AI-powered semantic matching between job descriptions and parsed resumes using sentence transformers and skill-based scoring.

## 📋 About This Module

This module provides **intelligent candidate-job matching** capabilities extracted from the complete TalentAI platform. It focuses on semantic understanding and skill-based compatibility scoring for hiring decisions.

For the **complete full-stack application** including frontend, backend, and full platform features, visit:
**[https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final](https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final)**

## Features

- **Semantic Matching**: Uses Sentence-BERT models for deep semantic understanding
- **Skill-Based Scoring**: Combines semantic similarity with Jaccard skill matching
- **Title Alignment**: Additional scoring based on job title similarity
- **FastAPI Integration**: Modern REST API with automatic documentation
- **Configuration Management**: Environment-based configuration system
- **CLI & API Modes**: Both command-line interface and HTTP API available

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the environment template and customize:

```bash
cp env.example .env
# Edit .env with your preferred settings
```

### 3. Run the System

#### Option A: Start FastAPI Server
```bash
python main.py --api
```

The API will be available at `http://localhost:8001`

#### Option B: Run CLI Demo
```bash
python main.py --resumes-dir ../resume_generator_parser/example_output/parsed
```

## API Usage

### Health Check
```bash
curl http://localhost:8001/health
```

### Match Candidates
```bash
curl -X POST http://localhost:8001/match \
  -H "Content-Type: application/json" \
  -d '{
    "job": {
      "title": "Software Engineer",
      "company": "TechCorp",
      "description": "We are looking for a software engineer...",
      "requirements": ["Python", "JavaScript", "3+ years experience"],
      "preferred_skills": ["Docker", "AWS"]
    },
    "top_n": 5
  }'
```

### Upload Job File
```bash
curl -X POST http://localhost:8001/match-file \
  -F "job_file=@job_description.json" \
  -F "top_n=5"
```

## Configuration

The system uses environment variables for configuration:

| Variable | Default | Description |
|----------|---------|-------------|
| `CANDIDATE_SBERT_MODEL` | `sentence-transformers/all-mpnet-base-v2` | Sentence transformer model |
| `CANDIDATE_DEVICE` | `cpu` | Device for model inference |
| `CANDIDATE_BLEND_ALPHA` | `0.25` | Weight for skills vs semantic similarity |
| `CANDIDATE_TITLE_WEIGHT` | `0.10` | Weight for title alignment |
| `CANDIDATE_API_PORT` | `8001` | API server port |
| `CANDIDATE_DEFAULT_RESUMES_DIR` | `../resume_generator_parser/example_output/parsed` | Default resumes directory |

## Data Format

### Job Description
```json
{
  "title": "Software Engineer",
  "company": "TechCorp Inc.",
  "description": "Job description text...",
  "requirements": ["Python", "JavaScript", "3+ years"],
  "preferred_skills": ["Docker", "AWS"]
}
```

### Expected Resume Data
The system expects parsed resume JSONs from the `resume_generator_parser` project:

- Individual resume files: `*.json` (excluding `*.error.json`)
- Combined file: `combined.json` with `results` array
- Each resume should have a `data` field containing the parsed resume structure

## Architecture

### Core Components

1. **SemanticMatcher**: Main matching engine using sentence transformers
2. **API Layer**: FastAPI-based REST interface
3. **Configuration**: Environment-based configuration management
4. **CLI Interface**: Command-line demo and testing

### Matching Algorithm

The system combines three scoring methods:

1. **Semantic Similarity** (75% weight by default): Sentence-BERT embeddings
2. **Skill Matching** (25% weight by default): Jaccard similarity of skills
3. **Title Alignment** (10% weight by default): Token overlap in titles

Final score = (1-α) × semantic_sim + α × skill_sim + title_weight × title_sim

## Development

### Running Examples
```bash
# Run comprehensive examples
python example_usage.py

# Run integration examples
python integration_example.py

# Run CLI demo
python main.py --resumes-dir ../resume_generator_parser/example_output/parsed
```

### Development Mode
```bash
python main.py --api --reload
```

### Adding New Models
Update the `CANDIDATE_SBERT_MODEL` environment variable with any sentence transformer model from Hugging Face.

## Integration with Resume Parser

This system is designed to work with the `resume_generator_parser` project:

1. **Data Flow**: Resume parser → JSON output → Candidate matcher
2. **Port Separation**: Resume parser (8000), Candidate matcher (8001)
3. **Shared Data**: Both systems can access the same parsed resume directory

## Troubleshooting

### Common Issues

1. **Model Loading**: Ensure sufficient RAM for sentence transformer models
2. **Port Conflicts**: Change `CANDIDATE_API_PORT` if 8001 is occupied
3. **Resume Directory**: Verify the path in `CANDIDATE_DEFAULT_RESUMES_DIR`

### Logs
Check the console output for detailed logging information.

## 🌟 Hack Nation 2025

This module was built during the **Hack Nation 2025 TalentAI Challenge** - a hackathon focused on revolutionizing the hiring process through AI-powered talent matching.

**🏆 Complete Application Repository**: [https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final](https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final)

This standalone module focuses on **semantic candidate matching**, making it perfect for:
- Hiring platform integrations
- Job recommendation systems
- Resume matching engines
- AI-powered recruitment tools
- Educational and research purposes

## License

This project is part of the HackNation 2025 TalentAI Challenge.
