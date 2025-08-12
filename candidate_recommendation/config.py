"""
Configuration file for the candidate recommendation system.

This module manages all configuration settings for the system, including:
- Sentence transformer model selection
- Matching algorithm parameters
- API configuration
- Default paths and settings

Configuration is loaded from environment variables with sensible defaults.
Environment variables can be set in a .env file or directly in the shell.
"""

import os
from typing import Optional

class CandidateRecommendationConfig:
    """
    Configuration class for candidate recommendation system.
    
    This class centralizes all configuration options and provides
    a clean interface for accessing settings throughout the system.
    """
    
    def __init__(self):
        """
        Initialize configuration with values from environment variables.
        
        Sets sensible defaults for all configuration options and
        allows override through environment variables.
        """
        # Sentence Transformer Model Configuration
        self.sbert_model = os.getenv("CANDIDATE_SBERT_MODEL", "sentence-transformers/all-mpnet-base-v2")
        self.device = os.getenv("CANDIDATE_DEVICE", "cpu")  # Device: 'gpu' or 'cpu'
        
        # Matching Algorithm Parameters
        self.blend_alpha = float(os.getenv("CANDIDATE_BLEND_ALPHA", "0.25"))  # Weight for skills Jaccard vs embedding similarity
        self.title_weight = float(os.getenv("CANDIDATE_TITLE_WEIGHT", "0.10"))  # Extra weight for title alignment
        
        # Default Paths
        self.default_resumes_dir = os.getenv("CANDIDATE_DEFAULT_RESUMES_DIR", "../resume_generator_parser/example_output/parsed")
        self.default_top_n = int(os.getenv("CANDIDATE_DEFAULT_TOP_N", "10"))
        
        # API Configuration
        self.api_host = os.getenv("CANDIDATE_API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("CANDIDATE_API_PORT", "8001"))  # Different port from resume parser
        self.api_debug = os.getenv("CANDIDATE_API_DEBUG", "false").lower() == "true"

# Create global configuration instance
# This instance is imported throughout the system to access configuration
config = CandidateRecommendationConfig()
