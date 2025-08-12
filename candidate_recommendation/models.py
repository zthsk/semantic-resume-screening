from dataclasses import dataclass
from typing import List

@dataclass
class JobDescription:
    """Job posting information."""
    title: str
    company: str
    description: str
    requirements: List[str]
    preferred_skills: List[str] = None

    def __post_init__(self):
        if self.preferred_skills is None:
            self.preferred_skills = []

@dataclass
class CandidateMatch:
    """Candidate match result."""
    name: str
    filename: str
    title: str
    match_score: float
    skills_match: List[str]
    summary: str
