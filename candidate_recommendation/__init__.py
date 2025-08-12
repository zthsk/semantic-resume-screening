"""
Candidate Recommendation System for semantic matching between job descriptions and resumes.
"""

from .models import JobDescription, CandidateMatch
from .semantic_matcher import SemanticMatcher

__all__ = ["JobDescription", "CandidateMatch", "SemanticMatcher"]
