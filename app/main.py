"""
Main FastAPI Application
Resume Analysis & Career Planning App
"""

import os
import json
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from resume_parser import parse_resume
from agent import run_agent
from youtube_search import get_video_recommendations, get_curated_channels
from sheets_export import generate_tsv_content
from sheets_api import (
    get_auth_url, 
    exchange_code_for_token, 
    is_authenticated,
    create_spreadsheet_with_data
)
from job_search import get_job_search_urls, get_job_tips
from interview_prep import get_interview_questions, get_interview_tips
from resume_analyzer import get_interview_questions_with_analysis
from cover_letter import generate_cover_letter
from pdf_generator import create_cover_letter_pdf, get_cover_letter_filename


# Initialize FastAPI app
app = FastAPI(
    title="Resume Analysis & Career Planning",
    description="Agentic AI-powered resume analysis and career guidance"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")

# In-memory session storage
session_data = {
    "resume_text": "",
    "role": "",
    "analysis": None,
    "oauth_state": None
}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the home page with resume upload form."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze", response_class=HTMLResponse)
async def analyze(
    request: Request,
    resume: UploadFile = File(...),
    role: str = Form(...)
):
    """Analyze the uploaded resume against the selected role."""
    try:
        resume_text = await parse_resume(resume)
        
        if not resume_text.strip():
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "error": "Could not extract text from the PDF. Please ensure the PDF contains readable text."
                }
            )
        
        session_data["resume_text"] = resume_text
        session_data["role"] = role
        
        analysis = await run_agent(resume_text, role)
        
        # Add YouTube recommendations
        roadmap_skills = analysis.get("roadmap", [])
        analysis["youtube_recommendations"] = get_video_recommendations(roadmap_skills, role)
        analysis["curated_channels"] = get_curated_channels(role)
        
        # Add Job Search URLs
        analysis["job_search_urls"] = get_job_search_urls(role)
        analysis["job_tips"] = get_job_tips(role)
        
        # Add Interview Prep
        analysis["interview_questions"] = get_interview_questions(role)
        analysis["interview_tips"] = get_interview_tips()
        
        # Generate TSV for clipboard export
        analysis["sheets_tsv"] = generate_tsv_content(analysis)
        
        # Check if user is authenticated with Google
        analysis["google_authenticated"] = is_authenticated()
        
        session_data["analysis"] = analysis
        
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "analysis": analysis
            }
        )
    
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": f"An error occurred during analysis: {str(e)}"
            }
        )


# ============ Google OAuth Routes ============

@app.get("/oauth/login")
async def oauth_login():
    """Start the OAuth flow - redirect to Google."""
    auth_url, state = get_auth_url()
    session_data["oauth_state"] = state
    return RedirectResponse(url=auth_url)


@app.get("/oauth/callback")
async def oauth_callback(request: Request, code: str = None, state: str = None, error: str = None):
    """Handle OAuth callback from Google."""
    if error:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": f"OAuth error: {error}"}
        )
    
    if code:
        try:
            exchange_code_for_token(code, state)
            # Redirect back to results if we have analysis data
            if session_data.get("analysis"):
                return RedirectResponse(url="/results")
            return RedirectResponse(url="/")
        except Exception as e:
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "error": f"OAuth failed: {str(e)}"}
            )
    
    return RedirectResponse(url="/")


@app.get("/results", response_class=HTMLResponse)
async def results(request: Request):
    """Re-render results page after OAuth."""
    analysis = session_data.get("analysis")
    if not analysis:
        return RedirectResponse(url="/")
    
    analysis["google_authenticated"] = is_authenticated()
    
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "analysis": analysis
        }
    )


@app.get("/oauth/status")
async def oauth_status():
    """Check if user is authenticated with Google."""
    return JSONResponse({"authenticated": is_authenticated()})


@app.post("/export/sheets")
async def export_to_sheets():
    """Export analysis directly to Google Sheets."""
    if not is_authenticated():
        return JSONResponse(
            {"success": False, "error": "Not authenticated", "need_auth": True},
            status_code=401
        )
    
    analysis = session_data.get("analysis")
    if not analysis:
        return JSONResponse(
            {"success": False, "error": "No analysis data"},
            status_code=400
        )
    
    result = create_spreadsheet_with_data(analysis)
    return JSONResponse(result)


# ============ Legacy Export ============

@app.get("/export/sheets-data")
async def export_sheets_data():
    """Return TSV data for clipboard copy (fallback)."""
    analysis = session_data.get("analysis")
    
    if not analysis:
        return JSONResponse({"error": "No analysis data available"}, status_code=400)
    
    return JSONResponse({
        "tsv": generate_tsv_content(analysis),
        "sheets_url": "https://docs.google.com/spreadsheets/create"
    })


# ============ Separate Pages ============

@app.get("/jobs", response_class=HTMLResponse)
async def jobs_page(request: Request):
    """Job Opportunities page."""
    analysis = session_data.get("analysis")
    if not analysis:
        return RedirectResponse(url="/")
    
    return templates.TemplateResponse(
        "jobs.html",
        {
            "request": request,
            "target_role": analysis.get("target_role", ""),
            "job_search_urls": analysis.get("job_search_urls", {}),
            "job_tips": analysis.get("job_tips", []),
            "strengths": analysis.get("strengths", [])
        }
    )


@app.get("/interview", response_class=HTMLResponse)
async def interview_page(request: Request):
    """Interview Prep page with LLM-powered resume-based questions."""
    analysis = session_data.get("analysis")
    resume_text = session_data.get("resume_text", "")
    
    if not analysis:
        return RedirectResponse(url="/")
    
    # LLM-powered resume analysis for personalized questions
    llm_analysis = get_interview_questions_with_analysis(
        resume_text,
        target_role=analysis.get("target_role", ""),
        strengths=analysis.get("strengths", []),
        skill_gaps=analysis.get("skill_gaps", {})
    )
    
    return templates.TemplateResponse(
        "interview.html",
        {
            "request": request,
            "target_role": analysis.get("target_role", ""),
            "interview_questions": analysis.get("interview_questions", {}),
            "interview_tips": analysis.get("interview_tips", []),
            "resume_questions": llm_analysis.get("personalized_questions", []),
            "resume_analysis": llm_analysis.get("resume_analysis", {}),
            "llm_powered": llm_analysis.get("llm_powered", False)
        }
    )


@app.get("/cover-letter", response_class=HTMLResponse)
async def cover_letter_page(request: Request):
    """Cover Letter Generator page."""
    analysis = session_data.get("analysis")
    
    if not analysis:
        return RedirectResponse(url="/")
    
    return templates.TemplateResponse(
        "cover_letter.html",
        {
            "request": request,
            "target_role": analysis.get("target_role", ""),
            "cover_letter": None
        }
    )


@app.post("/generate-cover-letter", response_class=HTMLResponse)
async def generate_cover_letter_route(
    request: Request,
    candidate_name: str = Form(...),
    company_name: str = Form(...),
    position: str = Form(...),
    job_description: str = Form(...)
):
    """Generate cover letter from resume and job description."""
    analysis = session_data.get("analysis")
    resume_text = session_data.get("resume_text", "")
    
    if not analysis or not resume_text:
        return RedirectResponse(url="/")
    
    # Generate cover letter using LLM
    result = generate_cover_letter(
        resume_text=resume_text,
        job_description=job_description,
        company_name=company_name,
        position=position,
        candidate_name=candidate_name
    )
    
    # Store for PDF download
    session_data["cover_letter_data"] = result
    
    return templates.TemplateResponse(
        "cover_letter.html",
        {
            "request": request,
            "target_role": position,
            "cover_letter": result.get("cover_letter", ""),
            "company": company_name,
            "position": position,
            "candidate_name": candidate_name
        }
    )


@app.get("/download-cover-letter")
async def download_cover_letter():
    """Download cover letter as PDF."""
    cover_letter_data = session_data.get("cover_letter_data")
    
    if not cover_letter_data:
        return RedirectResponse(url="/cover-letter")
    
    # Generate PDF
    pdf_content = create_cover_letter_pdf(cover_letter_data)
    
    # Get filename
    filename = get_cover_letter_filename(
        cover_letter_data.get("company", "Company"),
        cover_letter_data.get("position", "Position")
    )
    
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
