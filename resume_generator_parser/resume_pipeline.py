#!/usr/bin/env python3
"""
Complete Resume Pipeline: Generate, Parse, Summarize, and Save

This script demonstrates a complete workflow:
1. Generates synthetic resumes using the ResumeGenerator
2. Parses them using the ResumeParser
3. Generates summaries using Groq LLM
4. Saves all parsed information plus summaries to JSON files

Usage:
    python resume_pipeline_complete.py [--count N] [--output-dir DIR] [--groq-api-key KEY]
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import time

# Import from existing modules
from resume_generator import ResumeGenerator, ResumeRenderer
from resume_parser import get_parser
from llm_summarizer import get_summarizer
from models import ResumeStruct, ParsedResume

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CompleteResumePipeline:
    """
    Complete pipeline for generating, parsing, summarizing, and saving resumes.
    """
    
    def __init__(self, output_dir: Path, groq_api_key: str = None):
        """
        Initialize the pipeline.
        
        Args:
            output_dir: Directory to save generated files
            groq_api_key: Groq API key for summarization
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up components
        self.generator = ResumeGenerator(seed=42)  # Fixed seed for reproducibility
        self.parser = get_parser()
        self.summarizer = get_summarizer()
        
        # Set Groq as the preferred provider if API key is provided
        if groq_api_key:
            os.environ['GROQ_API_KEY'] = groq_api_key
            self.summarizer.set_provider('groq')
            logger.info("Set Groq as the summarization provider")
        
        # Create subdirectories
        self.resumes_dir = self.output_dir / "resumes"
        self.parsed_dir = self.output_dir / "parsed"
        self.summaries_dir = self.output_dir / "summaries"
        
        for dir_path in [self.resumes_dir, self.parsed_dir, self.summaries_dir]:
            dir_path.mkdir(exist_ok=True)
    
    def generate_resumes(self, count: int) -> List[ResumeStruct]:
        """
        Generate synthetic resumes.
        
        Args:
            count: Number of resumes to generate
            
        Returns:
            List of generated resume structures
        """
        logger.info(f"Generating {count} synthetic resumes...")
        resumes = self.generator.generate_multiple(count)
        logger.info(f"Generated {len(resumes)} resumes successfully")
        return resumes
    
    def save_resume_files(self, resumes: List[ResumeStruct]) -> List[Path]:
        """
        Save generated resumes as markdown files.
        
        Args:
            resumes: List of resume structures
            
        Returns:
            List of file paths where resumes were saved
        """
        file_paths = []
        
        for i, resume in enumerate(resumes):
            # Generate markdown content
            markdown_content = ResumeRenderer.to_markdown(resume)
            
            # Create filename
            safe_name = resume.name.replace(' ', '_').lower()
            filename = f"{safe_name}_{i+1:03d}.md"
            file_path = self.resumes_dir / filename
            
            # Save file
            file_path.write_text(markdown_content, encoding='utf-8')
            file_paths.append(file_path)
            logger.info(f"Saved resume: {file_path}")
        
        return file_paths
    
    def parse_resumes(self, file_paths: List[Path]) -> List[ResumeStruct]:
        """
        Parse resume files to extract structured data.
        
        Args:
            file_paths: List of resume file paths
            
        Returns:
            List of parsed resume structures
        """
        logger.info(f"Parsing {len(file_paths)} resume files...")
        parsed_resumes = []
        
        for file_path in file_paths:
            try:
                parsed_resume = self.parser.parse_file(file_path)
                parsed_resumes.append(parsed_resume)
                logger.info(f"Parsed: {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to parse {file_path.name}: {e}")
        
        logger.info(f"Successfully parsed {len(parsed_resumes)} resumes")
        return parsed_resumes
    
    def generate_summaries(self, resumes: List[ResumeStruct]) -> List[str]:
        """
        Generate summaries for resumes using Groq LLM.
        
        Args:
            resumes: List of resume structures
            
        Returns:
            List of generated summaries
        """
        logger.info(f"Generating summaries for {len(resumes)} resumes...")
        summaries = []
        
        for i, resume in enumerate(resumes):
            try:
                # Generate summary with focus on key achievements
                summary = self.summarizer.summarize_resume(
                    resume,
                    max_length=250,
                    focus_areas=["technical skills", "achievements", "experience"],
                    tone="professional"
                )
                summaries.append(summary)
                logger.info(f"Generated summary for resume {i+1}")
                
                # Add small delay to avoid rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Failed to generate summary for resume {i+1}: {e}")
                # Fallback summary
                fallback = f"Experienced {resume.title} with {len(resume.experience)} years of work experience. "
                fallback += f"Skilled in {', '.join(list(resume.skills.keys())[:3])}."
                summaries.append(fallback)
        
        logger.info(f"Generated {len(summaries)} summaries successfully")
        return summaries
    
    def save_parsed_data(self, resumes: List[ResumeStruct], summaries: List[str], 
                         original_files: List[Path]) -> List[Path]:
        """
        Save parsed resume data and summaries to JSON files.
        
        Args:
            resumes: List of parsed resume structures
            summaries: List of generated summaries
            original_files: List of original resume file paths
            
        Returns:
            List of JSON file paths where data was saved
        """
        json_files = []
        
        for i, (resume, summary, original_file) in enumerate(zip(resumes, summaries, original_files)):
            # Create ParsedResume object
            parsed_resume = ParsedResume(
                filename=original_file.name,
                parsed_at=datetime.utcnow(),
                data=resume,
                summary=summary,
                llm_provider=self.summarizer.get_current_provider_name(),
                llm_model="llama3-8b-8192"  # Default Groq model
            )
            
            # Save to JSON
            safe_name = resume.name.replace(' ', '_').lower()
            json_filename = f"{safe_name}_{i+1:03d}_parsed.json"
            json_path = self.parsed_dir / json_filename
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(parsed_resume.to_dict(), f, indent=2, ensure_ascii=False)
            
            json_files.append(json_path)
            logger.info(f"Saved parsed data: {json_path}")
        
        return json_files
    
    def save_summary_only(self, summaries: List[str], resume_names: List[str]) -> List[Path]:
        """
        Save summaries separately for easy access.
        
        Args:
            summaries: List of generated summaries
            resume_names: List of resume names
            
        Returns:
            List of summary file paths
        """
        summary_files = []
        
        for i, (summary, name) in enumerate(zip(summaries, resume_names)):
            safe_name = name.replace(' ', '_').lower()
            summary_filename = f"{safe_name}_{i+1:03d}_summary.txt"
            summary_path = self.summaries_dir / summary_filename
            
            summary_path.write_text(summary, encoding='utf-8')
            summary_files.append(summary_path)
            logger.info(f"Saved summary: {summary_path}")
        
        return summary_files
    
    def create_pipeline_report(self, stats: Dict[str, Any]) -> Path:
        """
        Create a comprehensive report of the pipeline execution.
        
        Args:
            stats: Pipeline execution statistics
            
        Returns:
            Path to the generated report file
        """
        report_path = self.output_dir / "pipeline_report.json"
        
        report = {
            "execution_time": datetime.utcnow().isoformat() + "Z",
            "pipeline_version": "1.0.0",
            "statistics": stats,
            "output_directories": {
                "resumes": str(self.resumes_dir),
                "parsed_data": str(self.parsed_dir),
                "summaries": str(self.summaries_dir)
            },
            "llm_provider": self.summarizer.get_current_provider_name(),
            "available_providers": self.summarizer.get_available_providers()
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Created pipeline report: {report_path}")
        return report_path
    
    def run_pipeline(self, count: int) -> Dict[str, Any]:
        """
        Run the complete pipeline.
        
        Args:
            count: Number of resumes to process
            
        Returns:
            Dictionary with pipeline execution results and statistics
        """
        start_time = time.time()
        
        try:
            # Step 1: Generate resumes
            resumes = self.generate_resumes(count)
            
            # Step 2: Save resume files
            resume_files = self.save_resume_files(resumes)
            
            # Step 3: Parse resumes
            parsed_resumes = self.parse_resumes(resume_files)
            
            # Step 4: Generate summaries
            summaries = self.generate_summaries(parsed_resumes)
            
            # Step 5: Save parsed data and summaries
            json_files = self.save_parsed_data(parsed_resumes, summaries, resume_files)
            summary_files = self.save_summary_only(summaries, [r.name for r in resumes])
            
            # Calculate statistics
            execution_time = time.time() - start_time
            stats = {
                "total_resumes": count,
                "successfully_generated": len(resumes),
                "successfully_parsed": len(parsed_resumes),
                "successfully_summarized": len(summaries),
                "execution_time_seconds": round(execution_time, 2),
                "files_created": {
                    "resume_files": len(resume_files),
                    "json_files": len(json_files),
                    "summary_files": len(summary_files)
                }
            }
            
            # Create pipeline report
            self.create_pipeline_report(stats)
            
            logger.info("Pipeline completed successfully!")
            logger.info(f"Total execution time: {execution_time:.2f} seconds")
            
            return {
                "success": True,
                "statistics": stats,
                "output_files": {
                    "resumes": resume_files,
                    "parsed_data": json_files,
                    "summaries": summary_files
                }
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Pipeline failed: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "execution_time_seconds": round(execution_time, 2)
            }

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Complete Resume Pipeline: Generate, Parse, Summarize, and Save"
    )
    parser.add_argument(
        "--count", 
        type=int, 
        default=5,
        help="Number of resumes to generate (default: 5)"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="./resume_pipeline_output",
        help="Output directory for generated files (default: ./resume_pipeline_output)"
    )
    parser.add_argument(
        "--groq-api-key", 
        type=str,
        help="Groq API key for LLM summarization"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check for Groq API key
    if not args.groq_api_key:
        groq_key = os.environ.get('GROQ_API_KEY')
        if not groq_key:
            logger.warning("No Groq API key provided. Summaries will use fallback text.")
            logger.warning("Set GROQ_API_KEY environment variable or use --groq-api-key")
        else:
            args.groq_api_key = groq_key
    
    # Create output directory
    output_dir = Path(args.output_dir)
    
    try:
        # Initialize and run pipeline
        pipeline = CompleteResumePipeline(output_dir, args.groq_api_key)
        results = pipeline.run_pipeline(args.count)
        
        if results["success"]:
            print("\n" + "="*60)
            print("PIPELINE COMPLETED SUCCESSFULLY!")
            print("="*60)
            print(f"Generated {results['statistics']['total_resumes']} resumes")
            print(f"Parsed {results['statistics']['successfully_parsed']} resumes")
            print(f"Generated {results['statistics']['successfully_summarized']} summaries")
            print(f"Execution time: {results['statistics']['execution_time_seconds']} seconds")
            print(f"Output directory: {output_dir.absolute()}")
            print("="*60)
            
            # Print file locations
            print("\nGenerated files:")
            for category, files in results["output_files"].items():
                print(f"\n{category.upper()}:")
                for file_path in files:
                    print(f"  - {file_path.name}")
        else:
            print(f"\nPipeline failed: {results['error']}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
