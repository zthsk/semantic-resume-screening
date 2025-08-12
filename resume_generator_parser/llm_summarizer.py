"""
LLM-based resume summarization module.

This module provides an abstraction layer for different LLM providers (Groq API and local models)
to generate professional resume summaries. It implements a provider pattern that allows
easy switching between different LLM services and local models.

Key Features:
- Provider abstraction for different LLM services
- Automatic provider selection based on availability
- Fallback mechanisms when preferred providers fail
- Support for both cloud (Groq) and local models
- Consistent interface regardless of underlying provider

Usage:
    from llm_summarizer import get_summarizer
    
    summarizer = get_summarizer()
    summary = summarizer.summarize_resume(resume_data, max_length=200)
"""

import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

from config import config
from models import ResumeStruct, SummaryRequest

# Configure logging for this module
logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    This class defines the interface that all LLM providers must implement.
    It ensures consistency across different providers and makes it easy to
    add new providers in the future.
    """
    
    @abstractmethod
    def summarize(self, request: SummaryRequest) -> str:
        """
        Generate summary using the LLM.
        
        Args:
            request: SummaryRequest object containing resume data and parameters
            
        Returns:
            Generated summary text
            
        Raises:
            RuntimeError: If the provider is not available or summarization fails
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the provider is available for use.
        
        Returns:
            True if the provider can be used, False otherwise
        """
        pass

class GroqProvider(LLMProvider):
    """
    Groq API-based summarization provider.
    
    This provider uses Groq's cloud-based LLM service for fast and reliable
    resume summarization. It requires a valid GROQ_API_KEY to function.
    
    Features:
    - Fast inference with Groq's optimized models
    - Reliable cloud-based service
    - Cost-effective pricing
    - Support for various model sizes
    """
    
    def __init__(self):
        """
        Initialize the Groq provider.
        
        Attempts to create a Groq client and sets availability based on
        successful initialization and API key presence.
        """
        try:
            import groq
            self.client = groq.Groq(api_key=config.groq_api_key)
            self._available = True
            logger.info("Groq client initialized successfully")
        except ImportError:
            logger.warning("Groq library not installed. Install with: pip install groq")
            self._available = False
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            self._available = False
    
    def is_available(self) -> bool:
        """
        Check if Groq provider is available.
        
        Returns:
            True if Groq client is initialized and API key is set
        """
        return self._available and config.groq_api_key is not None
    
    def summarize(self, request: SummaryRequest) -> str:
        """
        Generate summary using Groq API.
        
        Args:
            request: SummaryRequest object containing resume data and parameters
            
        Returns:
            Generated summary text
            
        Raises:
            RuntimeError: If provider is not available or API call fails
        """
        if not self.is_available():
            raise RuntimeError("Groq provider not available")
        
        try:
            # Create the prompt for the LLM
            prompt = request.to_prompt()
            
            # Make API call to Groq
            response = self.client.chat.completions.create(
                model=config.groq_model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Based on the resume, provide a summary of the candidate's skills, experience, and education."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=config.groq_max_tokens,
                temperature=config.groq_temperature
            )
            
            # Extract and return the generated text
            summary = response.choices[0].message.content.strip()
            logger.info(f"Successfully generated summary with Groq ({len(summary)} chars)")
            return summary
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise RuntimeError(f"Failed to generate summary: {e}")


class LocalProvider(LLMProvider):
    """
    Local/Open source model summarization provider.
    
    This provider runs open-source LLM models locally using the Hugging Face
    transformers library. It supports both sequence-to-sequence and causal
    language models, making it flexible for different model types.
    
    Features:
    - Privacy: No data leaves your system
    - Cost: No API costs after initial setup
    - Customization: Full control over model and parameters
    - Offline: Works without internet connection
    
    Requirements:
    - Sufficient RAM/VRAM for model loading
    - Transformers and PyTorch installed
    - Local model files downloaded
    """

    def __init__(self):
        """
        Initialize the local provider.
        
        Attempts to import required libraries and sets availability flag.
        Model loading is deferred until first use to save memory.
        """
        self._available = False
        self._tok = None
        self._model = None
        self._is_encdec = False  # Is this an encoder-decoder model?
        self._is_chat = False    # Is this a chat model?
        
        try:
            # Import required libraries
            import torch
            from transformers import AutoConfig, AutoTokenizer, AutoModel, pipeline
            
            self._torch = torch
            self._AutoConfig = AutoConfig
            self._AutoTokenizer = AutoTokenizer
            self._AutoModel = AutoModel
            self._pipeline = pipeline
            self._available = True
            
            logger.info("Local provider dependencies imported successfully")
        except ImportError as e:
            logger.warning(f"Transformers/torch not installed: {e}")
            logger.info("Install with: pip install transformers torch sentencepiece")
            self._available = False

    def is_available(self) -> bool:
        """
        Check if local provider is available.
        
        Returns:
            True if dependencies are installed and model path is configured
        """
        if not self._available or not getattr(config, "local_model_path", None):
            return False
        
        # Check CUDA availability if GPU is requested
        if getattr(config, "local_device", "cpu") == "cuda":
            return self._torch.cuda.is_available()
        
        return True

    def _resolve_device(self):
        """
        Resolve the device to use for model inference.
        
        Returns:
            Device ID (0 for GPU, -1 for CPU)
        """
        dev = getattr(config, "local_device", "cpu")
        if dev == "cuda" and self._torch.cuda.is_available():
            return 0
        return -1

    def _load_model(self):
        """
        Load the local model and tokenizer.
        
        This method is called lazily when first needed to save memory.
        It detects the model type and sets up the appropriate pipeline.
        """
        if self._model is not None:
            return  # Already loaded
        
        model_path = getattr(config, "local_model_path", None)
        if not model_path:
            raise RuntimeError("Local model path not configured")
        
        try:
            logger.info(f"Loading local model from: {model_path}")
            
            # Load model configuration to determine type
            config_obj = self._AutoConfig.from_pretrained(model_path)
            self._is_encdec = hasattr(config_obj, "is_encoder_decoder") and config_obj.is_encoder_decoder
            
            # Load tokenizer
            self._tok = self._AutoTokenizer.from_pretrained(model_path)
            if self._tok.pad_token is None:
                self._tok.pad_token = self._tok.eos_token
            
            # Load model
            self._model = self._AutoModel.from_pretrained(
                model_path,
                device_map=self._resolve_device(),
                torch_dtype=self._torch.float16 if self._resolve_device() >= 0 else self._torch.float32
            )
            
            # Create pipeline based on model type
            if self._is_encdec:
                self._pipe = self._pipeline(
                    "summarization",
                    model=self._model,
                    tokenizer=self._tok,
                    device=self._resolve_device()
                )
            else:
                self._pipe = self._pipeline(
                    "text-generation",
                    model=self._model,
                    tokenizer=self._tok,
                    device=self._resolve_device()
                )
            
            logger.info(f"Local model loaded successfully (type: {'encoder-decoder' if self._is_encdec else 'causal'})")
            
        except Exception as e:
            logger.error(f"Failed to load local model: {e}")
            raise RuntimeError(f"Model loading failed: {e}")

    def _resume_to_text(self, resume: ResumeStruct) -> str:
        """
        Convert resume structure to plain text for LLM processing.
        
        Args:
            resume: ResumeStruct object to convert
            
        Returns:
            Plain text representation of the resume
        """
        lines = []
        
        # Basic information
        if resume.name:
            lines.append(f"Name: {resume.name}")
        if resume.title:
            lines.append(f"Title: {resume.title}")
        if resume.email:
            lines.append(f"Email: {resume.email}")
        if resume.phone:
            lines.append(f"Phone: {resume.phone}")
        if resume.location:
            lines.append(f"Location: {resume.location}")
        
        lines.append("")  # Empty line for separation
        
        # Education
        if resume.education:
            lines.append("Education:")
            for edu in resume.education:
                edu_text = f"- {edu.degree}"
                if edu.institution:
                    edu_text += f" from {edu.institution}"
                if edu.field_of_study:
                    edu_text += f" in {edu.field_of_study}"
                if edu.year:
                    edu_text += f" ({edu.year})"
                lines.append(edu_text)
            lines.append("")
        
        # Experience
        if resume.experience:
            lines.append("Experience:")
            for exp in resume.experience:
                exp_text = f"- {exp.title} at {exp.company}"
                if exp.start or exp.end:
                    period = f" ({exp.start or 'Start'} - {exp.end or 'Present'})"
                    exp_text += period
                if exp.location:
                    exp_text += f" in {exp.location}"
                lines.append(exp_text)
                
                if exp.highlights:
                    for highlight in exp.highlights:
                        lines.append(f"  * {highlight}")
            lines.append("")
        
        # Skills
        if resume.skills:
            lines.append("Skills:")
            for category, skills in resume.skills.items():
                if skills:
                    lines.append(f"- {category}: {', '.join(skills)}")
        
        return "\n".join(lines)

    def _build_prompt(self, resume_text: str) -> str:
        """
        Build a prompt for the local model.
        
        Args:
            resume_text: Plain text resume content
            
        Returns:
            Formatted prompt for the model
        """
        return f"""Please provide a professional summary of the following resume:

{resume_text}

Summary:"""

    def _chat_prompt(self, resume_text: str) -> str:
        """
        Build a chat-style prompt for models that expect conversation format.
        
        Args:
            resume_text: Plain text resume content
            
        Returns:
            Chat-formatted prompt
        """
        return f"""<|im_start|>system
You are a professional resume analyst. Provide concise, professional summaries of candidate resumes.
<|im_end|>
<|im_start|>user
Please summarize this resume: {resume_text}
<|im_end|>
<|im_start|>assistant
"""

    def summarize(self, request: SummaryRequest) -> str:
        """
        Generate summary using the local model.
        
        Args:
            request: SummaryRequest object containing resume data and parameters
            
        Returns:
            Generated summary text
            
        Raises:
            RuntimeError: If provider is not available or summarization fails
        """
        if not self.is_available():
            raise RuntimeError("Local provider not available")

        # Load model if not already loaded
        self._load_model()
        
        # Convert resume to text
        resume_text = self._resume_to_text(request.resume_data)

        # Generate summary based on model type
        if self._is_encdec:
            # Use summarization pipeline for encoder-decoder models
            result = self._pipe(
                self._build_prompt(resume_text),
                max_length=min(getattr(request, "max_length", 120), 200),
                min_length=40,
                do_sample=False,
                truncation=True
            )
            summary = result[0]["generated_text"].strip()
        else:
            # Use text generation pipeline for causal models
            prompt = self._chat_prompt(resume_text) if self._is_chat else self._build_prompt(resume_text)
            result = self._pipe(
                prompt,
                max_new_tokens=min(getattr(request, "max_length", 160), 256),
                do_sample=False,
                temperature=0.0,
                eos_token_id=getattr(self._tok, "eos_token_id", None),
                pad_token_id=getattr(self._tok, "eos_token_id", None),
                truncation=True
            )[0]["generated_text"]

            # Clean up the generated text
            if result.startswith(prompt):
                result = result[len(prompt):]

            if "Summary:" in result:
                result = result.split("Summary:", 1)[-1].strip()

            summary = " ".join(result.strip().split()[:50])  # Quick length control
        
        logger.info(f"Successfully generated summary with local model ({len(summary)} chars)")
        return summary


class LLMSummarizer:
    """
    Main summarizer class that manages different LLM providers.
    
    This class implements a provider pattern that allows easy switching between
    different LLM services. It automatically selects the best available provider
    and provides a consistent interface for summarization.
    
    Features:
    - Automatic provider selection based on availability
    - Easy provider switching
    - Fallback mechanisms
    - Consistent interface across providers
    """
    
    def __init__(self):
        """
        Initialize the summarizer with available providers.
        
        Creates provider instances and automatically selects the best available
        provider based on configuration and availability.
        """
        # Initialize all available providers
        self.providers = {
            "groq": GroqProvider(),
            "local": LocalProvider()
        }
        self._current_provider = None
        
        # Auto-select provider based on configuration
        try:
            from config import config
            preferred_provider = config.provider
            
            # Try to use the preferred provider if it's available
            if preferred_provider in self.providers and self.providers[preferred_provider].is_available():
                self._current_provider = self.providers[preferred_provider]
                logger.info(f"Auto-selected preferred provider: {preferred_provider}")
            else:
                # Fallback to first available provider
                for name, provider in self.providers.items():
                    if provider.is_available():
                        self._current_provider = provider
                        logger.info(f"Fallback to provider: {name}")
                        break
                        
        except Exception as e:
            logger.warning(f"Could not auto-select provider: {e}")
            # Fallback to first available provider
            for name, provider in self.providers.items():
                if provider.is_available():
                    self._current_provider = provider
                    logger.info(f"Fallback to provider: {name}")
                    break
    
    def set_provider(self, provider_name: str) -> None:
        """
        Set the current LLM provider.
        
        Args:
            provider_name: Name of the provider to use ('groq' or 'local')
            
        Raises:
            ValueError: If provider name is unknown
            RuntimeError: If provider is not available
        """
        if provider_name not in self.providers:
            raise ValueError(f"Unknown provider: {provider_name}. Available: {list(self.providers.keys())}")
        
        provider = self.providers[provider_name]
        if not provider.is_available():
            raise RuntimeError(f"Provider {provider_name} is not available")
        
        self._current_provider = provider
        logger.info(f"Set LLM provider to: {provider_name}")
    
    def get_available_providers(self) -> Dict[str, bool]:
        """
        Get list of available providers and their status.
        
        Returns:
            Dictionary mapping provider names to availability status
        """
        return {name: provider.is_available() for name, provider in self.providers.items()}
    
    def get_current_provider_name(self) -> str:
        """
        Get the name of the current provider.
        
        Returns:
            Name of the current provider, or 'none' if no provider is set
        """
        if self._current_provider is None:
            return "none"
        
        for name, provider in self.providers.items():
            if provider is self._current_provider:
                return name
        
        return "unknown"
    
    def summarize(self, request: SummaryRequest) -> str:
        """
        Generate summary using the current provider.
        
        Args:
            request: SummaryRequest object containing resume data and parameters
            
        Returns:
            Generated summary text
            
        Raises:
            RuntimeError: If no providers are available or summarization fails
        """
        if self._current_provider is None:
            # Auto-select first available provider
            for name, provider in self.providers.items():
                if provider.is_available():
                    self._current_provider = provider
                    logger.info(f"Auto-selected provider: {name}")
                    break
            else:
                raise RuntimeError("No LLM providers available")
        
        return self._current_provider.summarize(request)
    
    def summarize_resume(self, resume: ResumeStruct, **kwargs) -> str:
        """
        Convenience method to summarize a resume.
        
        This method creates a SummaryRequest from the resume data and
        calls the main summarize method.
        
        Args:
            resume: ResumeStruct object to summarize
            **kwargs: Additional parameters for SummaryRequest
            
        Returns:
            Generated summary text
        """
        request = SummaryRequest(resume_data=resume, **kwargs)
        return self.summarize(request)


# Global summarizer instance for easy access
summarizer = LLMSummarizer()

def get_summarizer() -> LLMSummarizer:
    """
    Get the global summarizer instance.
    
    Returns:
        Global LLMSummarizer instance
    """
    return summarizer
