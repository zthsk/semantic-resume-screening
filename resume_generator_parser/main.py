"""
Main entry point for the resume parser and summarizer system.
Provides a clean interface for backend integration.
"""
import argparse
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from config import config
from models import ResumeStruct, ParsedResume
from resume_parser import get_parser
from llm_summarizer import get_summarizer
from resume_generator import generate_resumes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ResumeProcessor:
    """Main class for processing resumes with LLM summarization."""
    
    def __init__(self, llm_provider: Optional[str] = None):
        """Initialize the processor with optional LLM provider specification."""
        self.parser = get_parser()
        self.summarizer = get_summarizer()
        
        # Set LLM provider if specified
        if llm_provider:
            try:
                self.summarizer.set_provider(llm_provider)
                logger.info(f"Set LLM provider to: {llm_provider}")
            except Exception as e:
                logger.warning(f"Failed to set provider {llm_provider}: {e}")
                logger.info("Falling back to auto-selection")
    
    def process_resume_file(self, file_path: Path, **summary_kwargs) -> ParsedResume:
        """Process a single resume file and return parsed data with LLM summary."""
        logger.info(f"Processing resume file: {file_path}")
        
        # Parse the resume
        resume_data = self.parser.parse_file(file_path)
        
        # Generate summary using LLM
        try:
            summary = self.summarizer.summarize_resume(resume_data, **summary_kwargs)
            llm_provider = self.summarizer.get_current_provider_name()
            if llm_provider == "groq":
                llm_model = config.groq_model
            elif llm_provider == "local":
                llm_model = config.local_model_path or "local"
            else:
                llm_model = "unknown"
        except Exception as e:
            logger.error(f"LLM summarization failed: {e}")
            # Fallback to basic summary
            summary = self._generate_basic_summary(resume_data)
            llm_provider = "fallback"
            llm_model = "basic"
        
        return ParsedResume(
            filename=file_path.name,
            parsed_at=datetime.utcnow(),
            data=resume_data,
            summary=summary,
            llm_provider=llm_provider,
            llm_model=llm_model
        )
    
    def process_directory(self, input_dir: Path, output_dir: Path, 
                         file_pattern: str = "*.md", **summary_kwargs) -> List[ParsedResume]:
        """Process all matching files in a directory."""
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find matching files
        files = list(input_dir.glob(file_pattern))
        if not files:
            logger.warning(f"No files found matching pattern '{file_pattern}' in {input_dir}")
            return []
        
        logger.info(f"Found {len(files)} files to process")
        
        results = []
        for file_path in files:
            try:
                result = self.process_resume_file(file_path, **summary_kwargs)
                results.append(result)
                
                # Save individual result
                output_file = output_dir / f"{file_path.stem}.json"
                output_file.write_text(result.to_json(), encoding="utf-8")
                logger.info(f"Saved: {output_file}")
                
            except Exception as e:
                logger.error(f"Failed to process {file_path.name}: {e}")
        
        # Save combined results
        combined_file = output_dir / "combined_results.json"
        combined_data = {
            "processed_at": datetime.utcnow().isoformat() + "Z",
            "total_files": len(files),
            "successful_parses": len(results),
            "llm_provider": results[0].llm_provider if results else "unknown",
            "llm_model": results[0].llm_model if results else "unknown",
            "results": [r.to_dict() for r in results]
        }
        combined_file.write_text(json.dumps(combined_data, indent=2), encoding="utf-8")
        logger.info(f"Saved combined results: {combined_file}")
        
        return results
    
    def _generate_basic_summary(self, resume: ResumeStruct) -> str:
        """Generate a basic summary when LLM fails."""
        yrs = set()
        for exp in resume.experience:
            for token in (exp.start, exp.end):
                if token and token.strip() and token.strip() != "Present":
                    import re
                    m = re.search(r"(19|20)\d{2}", token)
                    if m:
                        yrs.add(int(m.group(0)))
        
        if yrs:
            span = f"{min(yrs)}–{max(yrs)}"
        else:
            span = "recent years"
        
        top_role = resume.title or (resume.experience[0].title if resume.experience else "Engineer")
        top_company = resume.experience[0].company if resume.experience else ""
        skill_flat = [s for group in resume.skills.values() for s in group]
        top_skills = ", ".join(sorted(skill_flat)[:5]) if skill_flat else None
        
        s1 = f"{resume.name} is a {top_role} based in {resume.location} with experience spanning {span}."
        s2 = f"Recent work includes roles at {top_company} delivering impact across multiple projects." if top_company else ""
        s3 = f"Core skills include {top_skills}." if top_skills else ""
        
        return " ".join([x for x in [s1, s2, s3] if x]).strip()
    
    def get_available_providers(self) -> Dict[str, bool]:
        """Get list of available LLM providers."""
        return self.summarizer.get_available_providers()
    
    def set_llm_provider(self, provider_name: str) -> None:
        """Set the LLM provider."""
        self.summarizer.set_provider(provider_name)

def main():
    """Main command-line interface."""
    parser = argparse.ArgumentParser(description="Resume Parser with LLM Summarization")
    parser.add_argument("--input", "-i", required=True, help="Input file or directory")
    parser.add_argument("--output", "-o", required=True, help="Output directory")
    parser.add_argument("--provider", "-p", help="LLM provider (groq, local)")
    parser.add_argument("--pattern", default="*.md", help="File pattern for directory processing")
    parser.add_argument("--max-length", type=int, default=200, help="Maximum summary length")
    parser.add_argument("--tone", choices=["professional", "casual", "technical"], default="professional", help="Summary tone")
    parser.add_argument("--focus", nargs="*", help="Focus areas for summary")
    parser.add_argument("--generate", type=int, help="Generate N synthetic resumes instead of parsing")
    parser.add_argument("--make-pdf", action="store_true", help="Generate PDFs for synthetic resumes")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if args.generate:
        # Generate synthetic resumes
        logger.info(f"Generating {args.generate} synthetic resumes")
        generate_resumes(output_path, args.generate, args.make_pdf)
        logger.info("✅ Resume generation complete")
        return
    
    if not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        return
    
    # Initialize processor
    processor = ResumeProcessor(args.provider)
    
    # Show available providers
    available = processor.get_available_providers()
    logger.info("Available LLM providers:")
    for provider, status in available.items():
        status_icon = "✅" if status else "❌"
        logger.info(f"  {status_icon} {provider}")
    
    # Process resumes
    if input_path.is_file():
        # Single file
        try:
            result = processor.process_resume_file(
                input_path,
                max_length=args.max_length,
                tone=args.tone,
                focus_areas=args.focus
            )
            
            # Save result
            output_path.mkdir(parents=True, exist_ok=True)
            output_file = output_path / f"{input_path.stem}.json"
            output_file.write_text(result.to_json(), encoding="utf-8")
            logger.info(f"✅ Processed single file: {output_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to process file: {e}")
    
    elif input_path.is_dir():
        # Directory
        try:
            results = processor.process_directory(
                input_path,
                output_path,
                args.pattern,
                max_length=args.max_length,
                tone=args.tone,
                focus_areas=args.focus
            )
            logger.info(f"✅ Processed {len(results)} files")
            
        except Exception as e:
            logger.error(f"❌ Failed to process directory: {e}")

if __name__ == "__main__":
    main()
