"""
Simple API interface for the resume parser and summarizer.
Provides HTTP endpoints for backend integration.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from models import ResumeStruct, ParsedResume, SummaryRequest
from resume_parser import get_parser
from llm_summarizer import get_summarizer
from resume_generator import generate_resumes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Resume Parser API",
    description="API for parsing resumes and generating LLM-powered summaries",
    version="1.0.0"
)

# Initialize components
parser = get_parser()
summarizer = get_summarizer()

# Request/Response models
class ParseRequest(BaseModel):
    content: str
    filename: Optional[str] = None
    max_length: int = 200
    tone: str = "professional"
    focus_areas: Optional[List[str]] = None

class ParseResponse(BaseModel):
    success: bool
    data: Optional[ParsedResume] = None
    error: Optional[str] = None
    processing_time: float

class BatchParseRequest(BaseModel):
    max_length: int = 200
    tone: str = "professional"
    focus_areas: Optional[List[str]] = None
    llm_provider: Optional[str] = None

class GenerateRequest(BaseModel):
    count: int = 10
    make_pdf: bool = False

class ProviderInfo(BaseModel):
    provider: str
    available: bool
    model: Optional[str] = None

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Resume Parser API",
        "version": "1.0.0",
        "endpoints": {
            "/parse": "Parse a single resume from text content",
            "/parse-file": "Parse a single resume file upload",
            "/parse-batch": "Parse multiple resume files from a directory",
            "/generate": "Generate synthetic resumes for testing",
            "/providers": "Get available LLM providers",
            "/health": "Health check endpoint"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/providers", response_model=List[ProviderInfo])
async def get_providers():
    """Get available LLM providers and their status."""
    available = summarizer.get_available_providers()
    providers = []
    
    for name, status in available.items():
        if name == "groq" and status:
            model = config.groq_model
        elif name == "local" and status:
            model = config.local_model_path or "local"
        else:
            model = None
            
        provider_info = ProviderInfo(
            provider=name,
            available=status,
            model=model
        )
        providers.append(provider_info)
    
    return providers

@app.post("/parse", response_model=ParseResponse)
async def parse_resume(request: ParseRequest):
    """Parse a resume from text content and generate summary."""
    start_time = datetime.utcnow()
    
    try:
        # Set LLM provider if specified
        if hasattr(request, 'llm_provider') and request.llm_provider:
            summarizer.set_provider(request.llm_provider)
        
        # Parse the resume content
        resume_data = parser.parse_markdown(request.content)
        
        # Generate summary
        summary = summarizer.summarize_resume(
            resume_data,
            max_length=request.max_length,
            tone=request.tone,
            focus_areas=request.focus_areas
        )
        
        # Get provider info
        llm_provider = summarizer.get_current_provider_name()
        if llm_provider == "groq":
            llm_model = config.groq_model
        elif llm_provider == "local":
            llm_model = config.local_model_path or "local"
        else:
            llm_model = "unknown"
        
        # Create response
        parsed_resume = ParsedResume(
            filename=request.filename or "uploaded_resume",
            parsed_at=datetime.utcnow(),
            data=resume_data,
            summary=summary,
            llm_provider=llm_provider,
            llm_model=str(llm_model)
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return ParseResponse(
            success=True,
            data=parsed_resume,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error parsing resume: {e}")
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return ParseResponse(
            success=False,
            error=str(e),
            processing_time=processing_time
        )

@app.post("/parse-file", response_model=ParseResponse)
async def parse_resume_file(
    file: UploadFile = File(...),
    max_length: int = Form(200),
    tone: str = Form("professional"),
    focus_areas: Optional[str] = Form(None),
    llm_provider: Optional[str] = Form(None)
):
    """Parse a resume from uploaded file and generate summary."""
    start_time = datetime.utcnow()
    
    try:
        # Read file content
        content = await file.read()
        text_content = content.decode('utf-8')
        
        # Parse focus areas if provided
        focus_list = None
        if focus_areas:
            focus_list = [area.strip() for area in focus_areas.split(',') if area.strip()]
        
        # Set LLM provider if specified
        if llm_provider:
            summarizer.set_provider(llm_provider)
        
        # Parse the resume
        resume_data = parser.parse_markdown(text_content)
        
        # Generate summary
        summary = summarizer.summarize_resume(
            resume_data,
            max_length=max_length,
            tone=tone,
            focus_areas=focus_list
        )
        
        # Get provider info
        llm_provider_name = summarizer.get_current_provider_name()
        if llm_provider_name == "groq":
            llm_model = config.groq_model
        elif llm_provider_name == "local":
            llm_model = config.local_model_path or "local"
        else:
            llm_model = "unknown"
        
        # Create response
        parsed_resume = ParsedResume(
            filename=file.filename,
            parsed_at=datetime.utcnow(),
            data=resume_data,
            summary=summary,
            llm_provider=llm_provider_name,
            llm_model=str(llm_model)
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return ParseResponse(
            success=True,
            data=parsed_resume,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error parsing file: {e}")
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return ParseResponse(
            success=False,
            error=str(e),
            processing_time=processing_time
        )

@app.post("/parse-batch")
async def parse_batch(
    request: BatchParseRequest,
    input_dir: str = Form(...),
    output_dir: str = Form(...)
):
    """Parse multiple resume files from a directory."""
    try:
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            raise HTTPException(status_code=400, detail=f"Input directory does not exist: {input_dir}")
        
        # Set LLM provider if specified
        if request.llm_provider:
            summarizer.set_provider(request.llm_provider)
        
        # Find markdown files
        files = list(input_path.glob("*.md"))
        if not files:
            raise HTTPException(status_code=400, detail=f"No markdown files found in {input_dir}")
        
        results = []
        for file_path in files:
            try:
                # Parse file
                resume_data = parser.parse_file(file_path)
                
                # Generate summary
                summary = summarizer.summarize_resume(
                    resume_data,
                    max_length=request.max_length,
                    tone=request.tone,
                    focus_areas=request.focus_areas
                )
                
                # Get provider info
                llm_provider = summarizer.get_current_provider_name()
                if llm_provider == "groq":
                    llm_model = config.groq_model
                elif llm_provider == "local":
                    llm_model = config.local_model_path or "local"
                else:
                    llm_model = "unknown"
                
                # Create result
                parsed_resume = ParsedResume(
                    filename=file_path.name,
                    parsed_at=datetime.utcnow(),
                    data=resume_data,
                    summary=summary,
                    llm_provider=llm_provider,
                    llm_model=str(llm_model)
                )
                
                results.append(parsed_resume)
                
            except Exception as e:
                logger.error(f"Failed to process {file_path.name}: {e}")
        
        # Save results
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save individual results
        for result in results:
            output_file = output_path / f"{Path(result.filename).stem}.json"
            output_file.write_text(result.to_json(), encoding="utf-8")
        
        # Save combined results
        combined_file = output_path / "combined_results.json"
        combined_data = {
            "processed_at": datetime.utcnow().isoformat() + "Z",
            "total_files": len(files),
            "successful_parses": len(results),
            "llm_provider": results[0].llm_provider if results else "unknown",
            "llm_model": results[0].llm_model if results else "unknown",
            "results": [r.to_dict() for r in results]
        }
        combined_file.write_text(json.dumps(combined_data, indent=2), encoding="utf-8")
        
        return {
            "success": True,
            "total_files": len(files),
            "successful_parses": len(results),
            "output_directory": str(output_path),
            "message": f"Processed {len(results)} out of {len(files)} files"
        }
        
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
async def generate_synthetic_resumes(request: GenerateRequest):
    """Generate synthetic resumes for testing."""
    try:
        output_dir = Path("/tmp/synthetic_resumes")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate resumes
        resumes = generate_resumes(output_dir, request.count, request.make_pdf)
        
        return {
            "success": True,
            "count": request.count,
            "output_directory": str(output_dir),
            "formats": ["markdown", "text"] + (["pdf"] if request.make_pdf else []),
            "message": f"Generated {len(resumes)} synthetic resumes"
        }
        
    except Exception as e:
        logger.error(f"Error generating resumes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/set-provider")
async def set_llm_provider(provider: str):
    """Set the LLM provider for summarization."""
    try:
        summarizer.set_provider(provider)
        return {
            "success": True,
            "provider": provider,
            "message": f"LLM provider set to {provider}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
