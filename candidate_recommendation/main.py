#!/usr/bin/env python3
"""
Main entry point for the Candidate Recommendation System.
Provides a clean interface for backend integration and CLI usage.
"""

import argparse
import logging
import uvicorn
from pathlib import Path
from typing import List

from config import config
from models import JobDescription
from semantic_matcher import SemanticMatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CandidateRecommendationProcessor:
    """Main class for processing candidate recommendations."""
    
    def __init__(self):
        """Initialize the processor with semantic matcher."""
        try:
            self.matcher = SemanticMatcher(
                sbert_model=config.sbert_model,
                device=config.device,
                blend_alpha=config.blend_alpha,
                title_weight=config.title_weight,
            )
            logger.info("✅ Semantic matcher initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize semantic matcher: {e}")
            raise
    
    def create_sample_jobs(self) -> List[JobDescription]:
        """Create sample job descriptions for testing."""
        # Software Engineer job
        software_job = JobDescription(
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

        # Data Scientist job
        data_job = JobDescription(
            title="Data Scientist",
            company="DataCorp",
            description="""
            Join our data science team to build machine learning models and 
            develop data-driven insights. You'll work with large datasets, 
            create predictive models, and help drive business decisions.
            """,
            requirements=[
                "3+ years of data science experience",
                "Strong Python programming skills",
                "Experience with machine learning libraries (scikit-learn, TensorFlow, PyTorch)",
                "Knowledge of statistics and mathematics",
                "Experience with SQL and data manipulation"
            ],
            preferred_skills=[
                "Deep learning",
                "Big data technologies (Spark, Hadoop)",
                "Cloud computing (AWS, GCP)",
                "Data visualization tools"
            ]
        )
        return [software_job, data_job]
    
    def match_candidates(self, job: JobDescription, resumes_dir: str, top_n: int = 10) -> List[dict]:
        """Match candidates to a job and return results."""
        logger.info(f"Matching candidates for: {job.title} at {job.company}")
        
        matches = self.matcher.match_candidates(job, resumes_dir, top_n=top_n)
        
        # Convert to dictionary format for easier handling
        results = []
        for match in matches:
            results.append({
                "name": match.name,
                "filename": match.filename,
                "title": match.title,
                "match_score": match.match_score,
                "skills_match": match.skills_match,
                "summary": match.summary
            })
        
        return results
    
    def run_cli_demo(self, resumes_dir: str, top_n: int):
        """Run the CLI demo with sample jobs."""
        logger.info("Running CLI demo with sample jobs")
        
        sample_jobs = self.create_sample_jobs()
        
        print("=" * 60)
        print("SEMANTIC MATCHING RESULTS")
        print("=" * 60)

        for job in sample_jobs:
            print(f"\n🔍 Job: {job.title} at {job.company}")
            print("-" * 50)
            
            try:
                matches = self.match_candidates(job, resumes_dir, top_n)
                
                for i, match in enumerate(matches, 1):
                    print(f"{i:2d}. {match['name']} ({match['title']})  score={match['match_score']:.3f}")
                    if match['skills_match']:
                        print(f"    Skills: {', '.join(match['skills_match'][:12])}")
                    print(f"    Summary: {match['summary']}\n")
                    
            except Exception as e:
                logger.error(f"Error matching candidates for {job.title}: {e}")
                print(f"    Error: {e}\n")

def main():
    """Main entry point for CLI usage."""
    ap = argparse.ArgumentParser(description="Candidate Recommendation Engine")
    ap.add_argument("--resumes-dir", default=config.default_resumes_dir,
                    help="Directory with parsed resume JSONs or a combined.json file")
    ap.add_argument("--top-n", type=int, default=config.default_top_n, 
                    help="How many candidates to show")
    ap.add_argument("--model", default=config.sbert_model,
                    help="Sentence-BERT model id")
    ap.add_argument("--blend-alpha", type=float, default=config.blend_alpha,
                    help="Weight for skills Jaccard vs embedding similarity (0..1)")
    ap.add_argument("--title-weight", type=float, default=config.title_weight,
                    help="Extra weight for JD vs candidate title alignment")
    ap.add_argument("--api", action="store_true", 
                    help="Start the FastAPI server instead of CLI demo")
    ap.add_argument("--host", default=config.api_host,
                    help="API server host (when using --api)")
    ap.add_argument("--port", type=int, default=config.api_port,
                    help="API server port (when using --api)")
    ap.add_argument("--reload", action="store_true",
                    help="Enable auto-reload for development (when using --api)")
    
    args = ap.parse_args()
    
    if args.api:
        # Start FastAPI server
        logger.info(f"Starting FastAPI server on {args.host}:{args.port}")
        uvicorn.run(
            "api:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info"
        )
    else:
        # Run CLI demo
        try:
            processor = CandidateRecommendationProcessor()
            processor.run_cli_demo(args.resumes_dir, args.top_n)
        except Exception as e:
            logger.error(f"Failed to run CLI demo: {e}")
            return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
