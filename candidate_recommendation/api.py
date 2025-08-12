"""
FastAPI interface for the Candidate Recommendation System.

This module provides a clean HTTP API for job-candidate matching,
following the same structure as the resume_generator_parser API.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from models import JobDescription, CandidateMatch
from semantic_matcher import SemanticMatcher
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Candidate Recommendation API",
    description="AI-powered semantic matching between jobs and candidates",
    version="1.0.0"
)

# Initialize the semantic matcher
try:
    matcher = SemanticMatcher(
        sbert_model=config.sbert_model,
        device=config.device,
        blend_alpha=config.blend_alpha,
        title_weight=config.title_weight,
    )
    logger.info("✅ Semantic matcher initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize semantic matcher: {e}")
    matcher = None

# Request/Response models
class JobMatchRequest(BaseModel):
    job: Dict[str, any]  # Job description data
    resumes_dir: Optional[str] = None
    top_n: Optional[int] = None

class JobMatchResponse(BaseModel):
    success: bool
    data: Optional[List[Dict[str, any]]] = None
    error: Optional[str] = None
    processing_time: float
    total_candidates: int

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    matcher: str
    model: str

class ModelsResponse(BaseModel):
    models: List[str]
    current_model: str

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Candidate Recommendation API",
        "version": "1.0.0",
        "description": "AI-powered semantic matching between jobs and candidates",
        "endpoints": {
            "/": "API information",
            "/health": "Health check",
            "/models": "Available models",
            "/match": "Match candidates to a job"
        },
        "usage": "Send POST requests to /match with job data to find candidate matches"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    if matcher is None:
        raise HTTPException(status_code=500, detail="Semantic matcher not initialized")
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        matcher="initialized",
        model=matcher.model_name if hasattr(matcher, 'model_name') else "unknown"
    )

@app.get("/models", response_model=ModelsResponse)
async def get_models():
    """List available sentence transformer models."""
    available_models = [
        "sentence-transformers/all-mpnet-base-v2",
        "sentence-transformers/all-MiniLM-L6-v2",
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    ]
    
    current_model = matcher.model_name if hasattr(matcher, 'model_name') else "unknown"
    
    return ModelsResponse(
        models=available_models,
        current_model=current_model
    )

@app.post("/match", response_model=JobMatchResponse)
async def match_candidates(request: JobMatchRequest):
    """Match candidates to a job description."""
    if matcher is None:
        raise HTTPException(status_code=500, detail="Semantic matcher not available")
    
    start_time = time.time()
    
    try:
        # Extract job data
        job_data = request.job
        resumes_dir = request.resumes_dir or config.default_resumes_dir
        top_n = request.top_n or config.default_top_n
        
        # Validate required fields
        required_fields = ['title', 'description', 'requirements']
        missing_fields = [field for field in required_fields if not job_data.get(field)]
        if missing_fields:
            raise HTTPException(status_code=400, detail=f"Missing required fields: {missing_fields}")
        
        # Create JobDescription object
        job = JobDescription(
            title=job_data.get('title', ''),
            company=job_data.get('company', ''),
            description=job_data.get('description', ''),
            requirements=job_data.get('requirements', []),
            preferred_skills=job_data.get('preferred_skills', [])
        )
        
        # Perform matching
        matches = matcher.match_candidates(job, resumes_dir, top_n=top_n)
        
        # Convert matches to dictionaries for JSON response
        match_data = []
        for match in matches:
            match_data.append({
                "name": match.name,
                "filename": match.filename,
                "title": match.title,
                "match_score": match.match_score,
                "skills_match": match.skills_match,
                "summary": match.summary
            })
        
        processing_time = time.time() - start_time
        
        return JobMatchResponse(
            success=True,
            data=match_data,
            error=None,
            processing_time=processing_time,
            total_candidates=len(match_data)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during candidate matching: {e}")
        processing_time = time.time() - start_time
        
        return JobMatchResponse(
            success=False,
            data=None,
            error=str(e),
            processing_time=processing_time,
            total_candidates=0
        )

@app.post("/match-file")
async def match_candidates_file(
    job_file: UploadFile = File(...),
    resumes_dir: Optional[str] = Form(None),
    top_n: Optional[int] = Form(None)
):
    """Match candidates to a job description from uploaded file."""
    if matcher is None:
        raise HTTPException(status_code=500, detail="Semantic matcher not available")
    
    start_time = time.time()
    
    try:
        # Read and parse job file
        content = await job_file.read()
        try:
            job_data = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON file")
        
        resumes_dir = resumes_dir or config.default_resumes_dir
        top_n = top_n or config.default_top_n
        
        # Validate required fields
        required_fields = ['title', 'description', 'requirements']
        missing_fields = [field for field in required_fields if not job_data.get(field)]
        if missing_fields:
            raise HTTPException(status_code=400, detail=f"Missing required fields: {missing_fields}")
        
        # Create JobDescription object
        job = JobDescription(
            title=job_data.get('title', ''),
            company=job_data.get('company', ''),
            description=job_data.get('description', ''),
            requirements=job_data.get('requirements', []),
            preferred_skills=job_data.get('preferred_skills', [])
        )
        
        # Perform matching
        matches = matcher.match_candidates(job, resumes_dir, top_n=top_n)
        
        # Convert matches to dictionaries for JSON response
        match_data = []
        for match in matches:
            match_data.append({
                "name": match.name,
                "filename": match.filename,
                "title": match.title,
                "match_score": match.match_score,
                "skills_match": match.skills_match,
                "summary": match.summary
            })
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "data": match_data,
            "error": None,
            "processing_time": processing_time,
            "total_candidates": len(match_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during candidate matching: {e}")
        processing_time = time.time() - start_time
        
        return {
            "success": False,
            "data": None,
            "error": str(e),
            "processing_time": processing_time,
            "total_candidates": 0
        }

@app.exception_handler(404)
async def not_found(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "detail": "The requested endpoint does not exist"}
    )

@app.exception_handler(500)
async def internal_error(request, exc):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"}
    )
