"""
Data models for resume parsing and summarization.
"""
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Literal
from datetime import datetime
import json

@dataclass
class Education:
    """Education information from resume."""
    institution: str
    degree: str
    field_of_study: str
    year: int
    gpa: Optional[float] = None
    location: Optional[str] = None

@dataclass
class Experience:
    """Work experience information from resume."""
    company: str
    title: str
    start: str  # e.g., "Jan 2021"
    end: str    # e.g., "Present" or "Jun 2023"
    location: str
    highlights: List[str]

@dataclass
class ResumeStruct:
    """Complete resume structure."""
    name: str
    title: str
    email: str
    phone: str
    location: str
    education: List[Education]
    experience: List[Experience]
    skills: Dict[str, List[str]]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

@dataclass
class ParsedResume:
    """Parsed resume with metadata."""
    filename: str
    parsed_at: datetime
    data: ResumeStruct
    summary: str
    llm_provider: str
    llm_model: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "filename": self.filename,
            "parsed_at": self.parsed_at.isoformat() + "Z",
            "data": self.data.to_dict(),
            "summary": self.summary,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

@dataclass
class SummaryRequest:
    """Request for resume summarization."""
    resume_data: ResumeStruct
    max_length: int = 200
    focus_areas: Optional[List[str]] = None
    tone: Literal["professional", "casual", "technical"] = "professional"
    
    def to_prompt(self) -> str:
        """Convert to LLM prompt."""
        focus_text = ""
        if self.focus_areas:
            focus_text = f"\nFocus on: {', '.join(self.focus_areas)}"
        
        return f"""Please provide a {self.max_length}-word summary of this candidate's resume. Don't place any placeholders and don't provide any other text that is not part of the summary.

{focus_text}
Tone: {self.tone}

Resume Data:
{json.dumps(self.resume_data.to_dict(), indent=2)}

Summary:"""
