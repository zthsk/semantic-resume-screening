#!/usr/bin/env python3
"""
Example usage of the CompleteResumePipeline class.

This script demonstrates how to use the pipeline programmatically
instead of running it from the command line.
"""

import os
from pathlib import Path
from resume_pipeline import CompleteResumePipeline

def main():
    """Example of using the pipeline programmatically."""
    
    # Set your Groq API key (or set GROQ_API_KEY environment variable)
    groq_api_key = os.environ.get('GROQ_API_KEY')  # or "your-api-key-here"
    
    # Create output directory
    output_dir = Path("./example_output")
    
    # Initialize the pipeline
    pipeline = CompleteResumePipeline(output_dir, groq_api_key)
    
    # Run the pipeline with 20 resumes
    print("Starting resume pipeline...")
    results = pipeline.run_pipeline(count=20)
    
    if results["success"]:
        print("\nPipeline completed successfully!")
        print(f"Generated {results['statistics']['successfully_generated']} resumes")
        print(f"Parsed {results['statistics']['successfully_parsed']} resumes")
        print(f"Generated {results['statistics']['successfully_summarized']} summaries")
        print(f"Execution time: {results['statistics']['execution_time_seconds']} seconds")
        
        # Access the generated files
        resume_files = results["output_files"]["resumes"]
        parsed_files = results["output_files"]["parsed_data"]
        summary_files = results["output_files"]["summaries"]
        
        print(f"\nGenerated files:")
        print(f"Resumes: {len(resume_files)} files")
        print(f"Parsed data: {len(parsed_files)} JSON files")
        print(f"Summaries: {len(summary_files)} text files")
        
        # Example: Read one of the parsed JSON files
        if parsed_files:
            import json
            with open(parsed_files[0], 'r') as f:
                parsed_data = json.load(f)
            
            print(f"\nSample parsed data from {parsed_files[0].name}:")
            print(f"Name: {parsed_data['data']['name']}")
            print(f"Title: {parsed_data['data']['title']}")
            print(f"Summary: {parsed_data['summary'][:100]}...")
            
    else:
        print(f"Pipeline failed: {results['error']}")

if __name__ == "__main__":
    main()
