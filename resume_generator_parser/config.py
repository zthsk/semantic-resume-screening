"""
Configuration file for the resume parser and summarizer system.

This module manages all configuration settings for the system, including:
- LLM provider selection (Groq API vs Local models)
- API keys and authentication
- Model parameters and settings
- Device configuration for local models

Configuration is loaded from environment variables with sensible defaults.
Environment variables can be set in a .env file or directly in the shell.
"""

import os
from typing import Optional

class LLMConfig:
    """
    Configuration class for LLM providers and settings.
    
    This class centralizes all configuration options and provides
    a clean interface for accessing settings throughout the system.
    """
    
    def __init__(self):
        """
        Initialize configuration with values from environment variables.
        
        Sets sensible defaults for all configuration options and
        allows override through environment variables.
        """
        # LLM Provider selection
        # Controls which LLM service to use: 'groq' for cloud API, 'local' for local models
        self.provider = os.getenv("RESUME_PROVIDER", "groq")
        
        # Groq API Configuration
        # These settings control the Groq cloud-based LLM service
        self.groq_api_key = os.getenv("GROQ_API_KEY")  # Required for Groq API access
        self.groq_model = os.getenv("RESUME_GROQ_MODEL", "llama3-8b-8192")  # Model to use
        self.groq_max_tokens = int(os.getenv("RESUME_GROQ_MAX_TOKENS", "500"))  # Max output length
        self.groq_temperature = float(os.getenv("RESUME_GROQ_TEMPERATURE", "0.3"))  # Creativity level (0.0-1.0)
        
        # Local/Open Source Model Configuration
        # These settings control local model inference
        self.local_model_path = os.getenv("RESUME_LOCAL_MODEL_PATH", "Qwen/Qwen2.5-7B-Instruct")  # Model path/name
        self.local_device = os.getenv("RESUME_LOCAL_DEVICE", "gpu")  # Device: 'gpu' or 'cpu'
        self.local_max_tokens = int(os.getenv("RESUME_LOCAL_MAX_TOKENS", "500"))  # Max output length
        self.local_temperature = float(os.getenv("RESUME_LOCAL_TEMPERATURE", "0.3"))  # Creativity level (0.0-1.0)

# Create global configuration instance
# This instance is imported throughout the system to access configuration
config = LLMConfig()

# Ensure API keys are properly loaded from environment
# This handles cases where environment variables might be set after import
if not config.groq_api_key:
    config.groq_api_key = os.getenv("GROQ_API_KEY")
