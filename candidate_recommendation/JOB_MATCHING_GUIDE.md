# Job-Candidate Matching System Guide

> **🚀 This is a standalone repository that's part of the [Hack Nation 2025 TalentAI Challenge](https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final)**

## 📋 About This Module

This module provides **comprehensive job-candidate matching guidance** extracted from the complete TalentAI platform. It focuses on semantic matching algorithms and integration patterns for hiring decisions.

For the **complete full-stack application** including frontend, backend, and full platform features, visit:
**[https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final](https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final)**

## Overview

Yes! The system **can absolutely send a job description and match it with candidates**. This is the core functionality of the Candidate Recommendation System.

## How It Works

### 1. **Job Description Input**
You provide a job description with:
- **Title**: Job title (e.g., "Senior Data Engineer")
- **Company**: Company name
- **Description**: Detailed job description
- **Requirements**: List of required skills/qualifications
- **Preferred Skills**: Optional preferred skills

### 2. **Candidate Matching Process**
The system uses **semantic matching** to find the best candidates:

1. **Text Embedding**: Converts job description and candidate resumes to vector representations
2. **Semantic Similarity**: Calculates cosine similarity between job and candidate vectors
3. **Skills Matching**: Uses Jaccard similarity for skills overlap
4. **Title Alignment**: Considers job title relevance
5. **Blended Scoring**: Combines all factors for final ranking

### 3. **Output Results**
Returns ranked list of candidates with:
- **Match Score**: Overall compatibility (0.0 to 1.0)
- **Candidate Details**: Name, current title, skills
- **Skills Match**: Specific skills that align with the job
- **Summary**: Candidate background summary

## Usage Examples

### Option 1: Python Script
```python
from models import JobDescription
from semantic_matcher import SemanticMatcher

# Create job description
job = JobDescription(
    title="Python Developer",
    company="TechCorp",
    description="Build web applications using Python",
    requirements=["Python", "Web frameworks", "Database"],
    preferred_skills=["Django", "FastAPI"]
)

# Initialize matcher
matcher = SemanticMatcher()

# Find matches
matches = matcher.match_candidates(job, "path/to/resumes", top_n=5)

# View results
for match in matches:
    print(f"{match.name}: {match.match_score:.3f}")
```

### Option 2: REST API
```bash
# Start the API server
python start_api.py

# Send POST request
curl -X POST http://localhost:5000/match \
  -H "Content-Type: application/json" \
  -d '{
    "job": {
      "title": "Data Scientist",
      "company": "DataCorp",
      "description": "Build ML models and analyze data",
      "requirements": ["Python", "Machine Learning", "Statistics"],
      "preferred_skills": ["TensorFlow", "SQL"]
    },
    "resumes_dir": "../resume_generator_parser/example_output/parsed",
    "top_n": 10
  }'
```

### Option 3: Integration Service
```python
from integration_example import CandidateRecommendationService

service = CandidateRecommendationService()
matches = service.find_candidates(job_data, resumes_path, top_n=10)
```

## Available Models

The system supports multiple sentence transformer models:
- `sentence-transformers/all-mpnet-base-v2` (default, best quality)
- `sentence-transformers/all-MiniLM-L6-v2` (faster, smaller)
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (multilingual)

## Scoring Algorithm

The final match score combines:
- **Semantic Similarity** (75% weight by default): Text embedding similarity
- **Skills Overlap** (20% weight by default): Jaccard similarity of skills
- **Title Alignment** (5% weight by default): Job title relevance

## 🌟 Hack Nation 2025

This module was built during the **Hack Nation 2025 TalentAI Challenge** - a hackathon focused on revolutionizing the hiring process through AI-powered talent matching.

**🏆 Complete Application Repository**: [https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final](https://github.com/poshan0126/hacknation-2025-talentai-challenge-10/tree/clean-repo-final)

This standalone module focuses on **job-candidate matching algorithms**, making it perfect for:
- Hiring platform integrations
- Job recommendation systems
- Resume matching engines
- AI-powered recruitment tools
- Educational and research purposes

## License

This project is part of the HackNation 2025 TalentAI Challenge.
