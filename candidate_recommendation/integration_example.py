#!/usr/bin/env python3
"""
Simple integration example for the Candidate Recommendation System.

This file shows how to easily integrate the candidate recommendation system
into existing applications with minimal code changes.
"""

from models import JobDescription
from semantic_matcher import SemanticMatcher

class CandidateRecommendationService:
    """
    A simple service class that wraps the candidate recommendation system
    for easy integration into existing applications.
    """
    
    def __init__(self, model_name="sentence-transformers/all-mpnet-base-v2"):
        """
        Initialize the recommendation service.
        
        Args:
            model_name (str): Name of the sentence transformer model to use
        """
        self.matcher = SemanticMatcher(sbert_model=model_name)
    
    def find_candidates(self, job_data, resumes_path, top_n=10):
        """
        Find top candidates for a job.
        
        Args:
            job_data (dict): Job description data with keys:
                - title: Job title
                - company: Company name
                - description: Job description
                - requirements: List of required skills
                - preferred_skills: List of preferred skills (optional)
            resumes_path (str): Path to directory containing parsed resumes
            top_n (int): Number of top candidates to return
            
        Returns:
            list: List of CandidateMatch objects sorted by score
        """
        # Convert dict to JobDescription object
        job = JobDescription(
            title=job_data.get("title", ""),
            company=job_data.get("company", ""),
            description=job_data.get("description", ""),
            requirements=job_data.get("requirements", []),
            preferred_skills=job_data.get("preferred_skills", [])
        )
        
        # Find matches
        matches = self.matcher.match_candidates(job, resumes_path, top_n=top_n)
        return matches
    
    def get_candidate_summary(self, matches):
        """
        Generate a summary of candidate matches.
        
        Args:
            matches (list): List of CandidateMatch objects
            
        Returns:
            dict: Summary statistics and insights
        """
        if not matches:
            return {"error": "No matches found"}
        
        # Calculate statistics
        total_candidates = len(matches)
        avg_score = sum(m.match_score for m in matches) / total_candidates
        max_score = max(m.match_score for m in matches)
        min_score = min(m.match_score for m in matches)
        
        # Get top skills
        all_skills = []
        for match in matches:
            if match.skills_match:
                all_skills.extend(match.skills_match)
        
        # Count skill frequency
        skill_counts = {}
        for skill in all_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Top 5 most common skills
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_candidates": total_candidates,
            "score_range": {
                "min": min_score,
                "max": max_score,
                "average": round(avg_score, 3)
            },
            "top_skills": top_skills,
            "candidates": [
                {
                    "name": m.name,
                    "title": m.title,
                    "score": m.match_score,
                    "skills": m.skills_match[:5] if m.skills_match else []
                }
                for m in matches
            ]
        }

# Example usage functions
def example_integration():
    """Example of how to integrate the service into an existing application."""
    
    # Initialize the service
    recommendation_service = CandidateRecommendationService()
    
    # Example job data (could come from a form, API, or database)
    job_data = {
        "title": "Python Developer",
        "company": "TechStartup",
        "description": "We need a Python developer to build our backend services",
        "requirements": [
            "Python programming",
            "Web frameworks (Django/Flask)",
            "Database experience",
            "API development",
            "Git version control"
        ],
        "preferred_skills": [
            "AWS",
            "Docker",
            "Testing",
            "CI/CD"
        ]
    }
    
    # Path to parsed resumes (adjust as needed)
    resumes_path = "../resume_generator_parser/example_output/parsed"
    
    print("🔍 Finding candidates for:", job_data["title"])
    print("=" * 50)
    
    try:
        # Find candidates
        matches = recommendation_service.find_candidates(job_data, resumes_path, top_n=5)
        
        if matches:
            # Get summary
            summary = recommendation_service.get_candidate_summary(matches)
            
            print(f"Found {summary['total_candidates']} candidates")
            print(f"Score range: {summary['score_range']['min']:.3f} - {summary['score_range']['max']:.3f}")
            print(f"Average score: {summary['score_range']['average']}")
            print()
            
            print("Top Skills in Candidate Pool:")
            for skill, count in summary['top_skills']:
                print(f"  {skill}: {count} candidates")
            print()
            
            print("Top Candidates:")
            for i, candidate in enumerate(summary['candidates'], 1):
                print(f"{i}. {candidate['name']} ({candidate['title']})")
                print(f"   Score: {candidate['score']:.3f}")
                print(f"   Skills: {', '.join(candidate['skills'])}")
                print()
        else:
            print("No candidates found. Make sure you have parsed resumes available.")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have:")
        print("1. Installed dependencies: pip install -r requirements.txt")
        print("2. Generated parsed resumes using the resume parser")
        print("3. Set the correct path to your parsed resumes")

def simple_function_call():
    """Example of a simple function call for quick integration."""
    
    # Quick candidate search function
    def quick_search(job_title, skills, resumes_path="../resume_generator_parser/example_output/parsed"):
        """
        Quick search for candidates with specific skills.
        
        Args:
            job_title (str): Job title
            skills (list): List of required skills
            resumes_path (str): Path to parsed resumes
            
        Returns:
            list: Top 3 candidate matches
        """
        service = CandidateRecommendationService()
        
        job_data = {
            "title": job_title,
            "company": "Company",
            "description": f"Looking for {job_title} with skills: {', '.join(skills)}",
            "requirements": skills,
            "preferred_skills": []
        }
        
        return service.find_candidates(job_data, resumes_path, top_n=3)
    
    # Example usage
    print("🚀 Quick Search Example")
    print("=" * 30)
    
    try:
        # Quick search for Python developers
        matches = quick_search("Python Developer", ["Python", "Django", "SQL"])
        
        if matches:
            print(f"Found {len(matches)} Python developers:")
            for i, match in enumerate(matches, 1):
                print(f"{i}. {match.name} - Score: {match.match_score:.3f}")
        else:
            print("No matches found")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🔧 Candidate Recommendation System - Integration Examples")
    print("=" * 60)
    print()
    
    print("1. Full Service Integration:")
    print("-" * 30)
    example_integration()
    
    print("\n" + "=" * 60 + "\n")
    
    print("2. Simple Function Call:")
    print("-" * 30)
    simple_function_call()
