#!/usr/bin/env python3
"""
Comprehensive usage examples for the Candidate Recommendation System.

This file demonstrates various ways to integrate and use the candidate recommendation
system, from simple matching to advanced integration scenarios.
"""

import json
from pathlib import Path
from models import JobDescription
from semantic_matcher import SemanticMatcher

def example_1_basic_usage():
    """Example 1: Basic job-candidate matching."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Job-Candidate Matching")
    print("=" * 60)
    
    # Create a job description
    job = JobDescription(
        title="Senior Software Engineer",
        company="TechCorp Inc.",
        description="""
        We are looking for a Senior Software Engineer to join our growing team. 
        You will be responsible for designing, developing, and maintaining scalable 
        software solutions. You should have experience with modern web technologies, 
        cloud platforms, and be comfortable working in a fast-paced environment.
        """,
        requirements=[
            "5+ years of software development experience",
            "Proficiency in Python, JavaScript, or similar languages",
            "Experience with cloud platforms (AWS, Azure, or GCP)",
            "Knowledge of web frameworks and APIs",
            "Experience with databases and data processing"
        ],
        preferred_skills=[
            "Machine Learning experience",
            "Docker and Kubernetes",
            "Microservices architecture",
            "Agile development methodologies"
        ]
    )
    
    # Initialize the semantic matcher
    matcher = SemanticMatcher(
        sbert_model="sentence-transformers/all-mpnet-base-v2",
        blend_alpha=0.25,  # Weight for skills Jaccard vs embedding similarity
        title_weight=0.10,  # Extra weight for title alignment
    )
    
    # Path to parsed resumes (adjust this path as needed)
    resumes_path = "../resume_generator_parser/example_output/parsed"
    
    # Find top 5 matches
    matches = matcher.match_candidates(job, resumes_path, top_n=5)
    
    print(f"Job: {job.title} at {job.company}")
    print(f"Requirements: {', '.join(job.requirements[:3])}...")
    print(f"Preferred Skills: {', '.join(job.preferred_skills[:3])}...")
    print(f"\nTop {len(matches)} Matches:")
    print("-" * 50)
    
    for i, candidate in enumerate(matches, 1):
        print(f"{i}. {candidate.name} ({candidate.title})")
        print(f"   Score: {candidate.match_score:.3f}")
        if candidate.skills_match:
            print(f"   Matching Skills: {', '.join(candidate.skills_match[:5])}")
        print(f"   Summary: {candidate.summary[:100]}...")
        print()

def example_2_multiple_jobs():
    """Example 2: Matching multiple job types."""
    print("=" * 60)
    print("EXAMPLE 2: Multiple Job Types Matching")
    print("=" * 60)
    
    # Create multiple job descriptions
    jobs = [
        JobDescription(
            title="Data Scientist",
            company="DataCorp",
            description="Build machine learning models and develop data-driven insights",
            requirements=[
                "3+ years of data science experience",
                "Strong Python programming skills",
                "Experience with ML libraries (scikit-learn, TensorFlow)",
                "Knowledge of statistics and mathematics",
                "Experience with SQL and data manipulation"
            ],
            preferred_skills=[
                "Deep learning",
                "Big data technologies (Spark, Hadoop)",
                "Cloud computing (AWS, GCP)",
                "Data visualization tools"
            ]
        ),
        JobDescription(
            title="DevOps Engineer",
            company="CloudTech",
            description="Manage infrastructure and deployment pipelines",
            requirements=[
                "2+ years of DevOps experience",
                "Experience with Docker and Kubernetes",
                "Knowledge of cloud platforms (AWS, Azure, GCP)",
                "Experience with CI/CD pipelines",
                "Infrastructure as Code (Terraform, CloudFormation)"
            ],
            preferred_skills=[
                "Monitoring and logging (Prometheus, ELK)",
                "Security best practices",
                "Database administration",
                "Network configuration"
            ]
        )
    ]
    
    matcher = SemanticMatcher()
    resumes_path = "../resume_generator_parser/example_output/parsed"
    
    for job in jobs:
        print(f"\n🔍 Job: {job.title} at {job.company}")
        print("-" * 50)
        
        matches = matcher.match_candidates(job, resumes_path, top_n=3)
        
        for i, candidate in enumerate(matches, 1):
            print(f"{i:2d}. {candidate.name} ({candidate.title})  score={candidate.match_score:.3f}")
            if candidate.skills_match:
                print(f"    Skills: {', '.join(candidate.skills_match[:8])}")
            print(f"    Summary: {candidate.summary[:80]}...")

def example_3_custom_scoring():
    """Example 3: Custom scoring and filtering."""
    print("=" * 60)
    print("EXAMPLE 3: Custom Scoring and Filtering")
    print("=" * 60)
    
    job = JobDescription(
        title="Full Stack Developer",
        company="WebCorp",
        description="Develop modern web applications with React and Node.js",
        requirements=[
            "JavaScript/TypeScript",
            "React or similar frontend framework",
            "Node.js or similar backend framework",
            "Database experience (SQL or NoSQL)",
            "Git version control"
        ],
        preferred_skills=[
            "AWS or similar cloud platform",
            "Docker containerization",
            "Testing frameworks (Jest, Cypress)",
            "CI/CD experience"
        ]
    )
    
    # Initialize with custom scoring parameters
    matcher = SemanticMatcher(
        blend_alpha=0.4,      # Higher weight for skills matching
        title_weight=0.15,    # Higher weight for title alignment
    )
    
    resumes_path = "../resume_generator_parser/example_output/parsed"
    matches = matcher.match_candidates(job, resumes_path, top_n=10)
    
    # Custom filtering: only candidates with score > 0.5
    high_quality_matches = [c for c in matches if c.match_score > 0.5]
    
    print(f"Job: {job.title}")
    print(f"Total candidates found: {len(matches)}")
    print(f"High-quality matches (score > 0.5): {len(high_quality_matches)}")
    print("\nHigh-Quality Matches:")
    print("-" * 40)
    
    for i, candidate in enumerate(high_quality_matches, 1):
        print(f"{i}. {candidate.name} - Score: {candidate.match_score:.3f}")
        if candidate.skills_match:
            print(f"   Skills: {', '.join(candidate.skills_match[:6])}")

def example_4_integration_with_resume_parser():
    """Example 4: Integration with resume parser output."""
    print("=" * 60)
    print("EXAMPLE 4: Integration with Resume Parser")
    print("=" * 60)
    
    # Simulate getting parsed resumes from the resume parser
    def load_parsed_resumes(parser_output_dir):
        """Load resumes from the resume parser output directory."""
        parser_dir = Path(parser_output_dir)
        
        if not parser_dir.exists():
            print(f"Warning: Directory {parser_output_dir} not found")
            print("Make sure to run the resume parser first to generate parsed resumes")
            return []
        
        # Look for combined.json or individual resume files
        resumes = []
        
        # Try combined.json first
        combined_file = parser_dir / "combined.json"
        if combined_file.exists():
            try:
                with open(combined_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "results" in data:
                        resumes = data["results"]
                    else:
                        resumes = [data]
                print(f"Loaded {len(resumes)} resumes from combined.json")
            except Exception as e:
                print(f"Error loading combined.json: {e}")
        
        # If no combined.json, look for individual files
        if not resumes:
            json_files = list(parser_dir.glob("*.json"))
            json_files = [f for f in json_files if not f.name.endswith('.error.json')]
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r') as f:
                        resume_data = json.load(f)
                        resumes.append(resume_data)
                except Exception as e:
                    print(f"Error loading {json_file}: {e}")
            
            print(f"Loaded {len(resumes)} resumes from individual files")
        
        return resumes
    
    # Load resumes from parser output
    resumes = load_parsed_resumes("../resume_generator_parser/example_output/parsed")
    
    if not resumes:
        print("No resumes found. Please run the resume parser first.")
        return
    
    # Create a job that matches the loaded resumes
    job = JobDescription(
        title="Software Engineer",
        company="TechStartup",
        description="Join our fast-growing startup and build amazing products",
        requirements=[
            "Programming experience",
            "Problem-solving skills",
            "Team collaboration",
            "Learning mindset"
        ],
        preferred_skills=[
            "Web development",
            "Mobile development",
            "Cloud platforms",
            "Machine learning"
        ]
    )
    
    # Initialize matcher
    matcher = SemanticMatcher()
    
    # Match against the loaded resumes
    matches = matcher.match_candidates(job, "../resume_generator_parser/example_output/parsed", top_n=5)
    
    print(f"Job: {job.title} at {job.company}")
    print(f"Resumes loaded: {len(resumes)}")
    print(f"Top matches found: {len(matches)}")
    print("\nTop Matches:")
    print("-" * 30)
    
    for i, candidate in enumerate(matches, 1):
        print(f"{i}. {candidate.name}")
        print(f"   Title: {candidate.title}")
        print(f"   Score: {candidate.match_score:.3f}")
        print(f"   File: {candidate.filename}")
        if candidate.skills_match:
            print(f"   Skills: {', '.join(candidate.skills_match[:5])}")
        print()

def example_5_api_integration():
    """Example 5: How to integrate with the REST API."""
    print("=" * 60)
    print("EXAMPLE 5: REST API Integration")
    print("=" * 60)
    
    print("To use the candidate recommendation system via REST API:")
    print()
    print("1. Start the API server:")
    print("   cd candidate_recommendation")
    print("   python main.py --api")
    print()
    print("2. The API will be available at http://localhost:5000")
    print()
    print("3. Available endpoints:")
    print("   POST /match - Match candidates to a job")
    print("   GET /health - Health check")
    print("   GET /models - Available models")
    print()
    print("4. Example API usage:")
    print("""
   curl -X POST "http://localhost:5000/match" \\
     -H "Content-Type: application/json" \\
     -d '{
       "job": {
         "title": "Software Engineer",
         "company": "TechCorp",
         "description": "Build scalable applications",
         "requirements": ["Python", "JavaScript", "3+ years"],
         "preferred_skills": ["AWS", "Docker"]
       },
       "resumes_dir": "../resume_generator_parser/example_output/parsed",
       "top_n": 5
     }'
   """)
    print()
    print("5. The API returns JSON with candidate matches:")
    print("""
   {
     "matches": [
       {
         "name": "John Doe",
         "title": "Senior Developer",
         "match_score": 0.85,
         "skills_match": ["Python", "JavaScript"],
         "summary": "Experienced developer...",
         "filename": "john_doe.json"
       }
     ]
   }
   """)

def main():
    """Run all examples."""
    print("🚀 Candidate Recommendation System - Usage Examples")
    print("=" * 70)
    print()
    
    try:
        example_1_basic_usage()
        print()
        
        example_2_multiple_jobs()
        print()
        
        example_3_custom_scoring()
        print()
        
        example_4_integration_with_resume_parser()
        print()
        
        example_5_api_integration()
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have:")
        print("1. Installed dependencies: pip install -r requirements.txt")
        print("2. Generated parsed resumes using the resume parser")
        print("3. Set the correct path to your parsed resumes")

if __name__ == "__main__":
    main()
