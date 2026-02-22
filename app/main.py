"""
Main FastAPI Application
Resume Analysis & Career Planning App
"""

import os
import json
import csv
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from resume_parser import parse_resume, get_resume_preview
from resume_storage import save_resume
from agent import run_agent
from youtube_search import get_video_recommendations, get_curated_channels
from job_search import get_job_search_urls, get_job_tips, generate_job_strategy
from interview_prep import get_interview_questions, get_interview_tips
from resume_analyzer import get_interview_questions_with_analysis
from cover_letter import generate_cover_letter
from pdf_generator import create_cover_letter_pdf, get_cover_letter_filename
from report_generator import create_analysis_report, get_report_filename
from session_manager import (
    get_session, get_session_data, set_session_data,
    create_session, set_session_cookie, get_session_id,
    update_session
)
from rate_limiter import rate_limit

# Upload limits
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

ALLOWED_ROLES = [
    "Frontend Developer", "Backend Developer", "Full Stack Developer",
    "Data Analyst", "Data Engineer", "Machine Learning Engineer",
    "AI Engineer", "DevOps Engineer", "Cloud Engineer",
    "Cybersecurity Analyst", "Product Manager", "UX Designer"
]


# Storage configuration
FEEDBACK_FILE = Path(__file__).parent / "data" / "feedback.csv"
if not FEEDBACK_FILE.parent.exists():
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title="Resume Analysis & Career Planning",
    description="Agentic AI-powered resume analysis and career guidance"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")

# ============ Main Routes ============
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the home page with resume upload form."""
    # Check if a session already exists with an analysis
    analysis = get_session_data(request, "analysis")
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request, 
            "error": None,
            "has_existing_analysis": analysis is not None
        }
    )


@app.post("/analyze", response_class=HTMLResponse)
@rate_limit(requests=2, window_seconds=60)  # Max 2 resumes per minute
async def analyze(
    request: Request,
    resume: UploadFile = File(...),
    role: str = Form(...)
):
    """Analyze the uploaded resume against the selected role."""
    # Validate role
    if role not in ALLOWED_ROLES or len(role) > 50:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": "Invalid role selected. Please choose from the provided list."
            }
        )
        
    try:
        # Read file bytes for storage before parsing
        file_bytes = await resume.read()
        
        # Validate file size
        if len(file_bytes) > MAX_UPLOAD_SIZE:
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "error": f"File too large. Maximum size is {MAX_UPLOAD_SIZE // (1024*1024)}MB. Your file is {len(file_bytes) / (1024*1024):.1f}MB."
                }
            )
        
        # Validate file type
        if not (resume.filename or "").lower().endswith(".pdf"):
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "error": "Only PDF files are supported. Please upload a .pdf resume."
                }
            )
        
        await resume.seek(0)  # Reset for parser
        
        resume_text, page_count = await parse_resume(resume)
        
        if not resume_text.strip():
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "error": "Could not extract text from the PDF. Please ensure the PDF contains readable text."
                }
            )
        
        # Generate resume preview for verification
        resume_preview = get_resume_preview(resume_text, page_count)
        
        # Save resume to storage
        try:
            save_resume(
                file_bytes=file_bytes,
                original_filename=resume.filename or "resume.pdf",
                target_role=role,
                detected_name=resume_preview.get("detected_name"),
                detected_email=resume_preview.get("email"),
            )
        except Exception as storage_err:
            print(f"[Warning] Could not save resume: {storage_err}")
        
        # Create session for this user
        session_id = create_session()
        
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
        

        # Store in user-specific session
        update_session(session_id, {
            "resume_text": resume_text,
            "role": role,
            "analysis": analysis,
            "resume_preview": resume_preview,
        })
        
        response = templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "analysis": analysis,
                "resume_preview": resume_preview
            }
        )
        
        # Set session cookie so subsequent requests know this user
        set_session_cookie(response, session_id)
        return response
    
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": f"An error occurred during analysis: {str(e)}"
            }
        )


# ============ Results Page (re-render from session) ============

@app.get("/results", response_class=HTMLResponse)
async def results(request: Request):
    """Re-render results page from session data."""
    analysis = get_session_data(request, "analysis")
    if not analysis:
        return RedirectResponse(url="/")
    
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "analysis": analysis,
            "resume_preview": get_session_data(request, "resume_preview", {})
        }
    )


# ============ Report Download ============

@app.get("/download-report")
async def download_report(request: Request):
    """Download the career analysis as a formatted PDF report."""
    analysis = get_session_data(request, "analysis")
    print(f"[download-report] Session ID: {get_session_id(request)}")
    print(f"[download-report] Analysis found: {analysis is not None}")
    
    if not analysis:
        print("[download-report] No analysis data found, redirecting to /")
        return RedirectResponse(url="/")
    
    resume_preview = get_session_data(request, "resume_preview", {})
    
    try:
        pdf_bytes = create_analysis_report(analysis, resume_preview)
        target_role = analysis.get("target_role", "Report")
        filename = get_report_filename(target_role)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Report generation error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


# ============ Separate Pages ============

@app.get("/jobs", response_class=HTMLResponse)
async def jobs_page(request: Request):
    """Job Opportunities page with AI-powered strategy."""
    analysis = get_session_data(request, "analysis")
    resume_text = get_session_data(request, "resume_text", "")
    if not analysis:
        return RedirectResponse(url="/")
    
    # Check for cached strategy in session
    job_strategy = get_session_data(request, "job_strategy")
    
    if not job_strategy:
        # Generate AI-powered job search strategy
        job_strategy = generate_job_strategy(
            resume_text=resume_text,
            target_role=analysis.get("target_role", ""),
            strengths=analysis.get("strengths", []),
            skill_gaps=analysis.get("skill_gaps", {})
        )
        # Cache it
        set_session_data(request, "job_strategy", job_strategy)
    
    return templates.TemplateResponse(
        "jobs.html",
        {
            "request": request,
            "target_role": analysis.get("target_role", ""),
            "job_search_urls": analysis.get("job_search_urls", {}),
            "job_tips": analysis.get("job_tips", []),
            "strengths": analysis.get("strengths", []),
            "job_strategy": job_strategy
        }
    )


@app.get("/interview", response_class=HTMLResponse)
async def interview_page(request: Request):
    """Interview Prep page — loads instantly with static questions."""
    analysis = get_session_data(request, "analysis")
    
    if not analysis:
        return RedirectResponse(url="/")
    
    return templates.TemplateResponse(
        "interview.html",
        {
            "request": request,
            "target_role": analysis.get("target_role", ""),
            "interview_questions": analysis.get("interview_questions", {}),
            "interview_tips": analysis.get("interview_tips", []),
        }
    )


@app.post("/api/resume-questions")
@rate_limit(requests=3, window_seconds=60)  # Max 3 generations per minute
async def generate_resume_questions(request: Request):
    """AJAX endpoint: generate AI-powered resume-based questions on demand."""
    analysis = get_session_data(request, "analysis")
    resume_text = get_session_data(request, "resume_text", "")
    
    if not analysis or not resume_text:
        return JSONResponse({"error": "No session data"}, status_code=400)
    
    try:
        llm_analysis = get_interview_questions_with_analysis(
            resume_text,
            target_role=analysis.get("target_role", ""),
            strengths=analysis.get("strengths", []),
            skill_gaps=analysis.get("skill_gaps", {})
        )
        return JSONResponse({
            "questions": llm_analysis.get("personalized_questions", []),
            "resume_analysis": llm_analysis.get("resume_analysis", {}),
            "llm_powered": llm_analysis.get("llm_powered", False),
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/cover-letter", response_class=HTMLResponse)
async def cover_letter_page(request: Request):
    """Cover Letter Generator page."""
    analysis = get_session_data(request, "analysis")
    if not analysis:
        return RedirectResponse(url="/")
        
    resume_preview = get_session_data(request, "resume_preview", {})
    candidate_name = resume_preview.get("detected_name", "")
    
    return templates.TemplateResponse(
        "cover_letter.html",
        {
            "request": request,
            "target_role": analysis.get("target_role", ""),
            "form_candidate_name": candidate_name,
            "cover_letter": None,
            "error": None,
            "match_analysis": {},
            "llm_powered": False
        }
    )


@app.post("/generate-cover-letter", response_class=HTMLResponse)
@rate_limit(requests=5, window_seconds=60)  # Max 5 per minute
async def generate_cover_letter_route(
    request: Request,
    candidate_name: str = Form(...),
    company_name: str = Form(...),
    position: str = Form(...),
    job_description: str = Form(...)
):
    """Generate cover letter from resume and job description."""
    analysis = get_session_data(request, "analysis")
    resume_text = get_session_data(request, "resume_text", "")
    
    if not analysis or not resume_text:
        return RedirectResponse(url="/")
    
    try:
        # Generate cover letter using LLM
        result = generate_cover_letter(
            resume_text=resume_text,
            job_description=job_description,
            company_name=company_name,
            position=position,
            candidate_name=candidate_name
        )
        
        # Check for generation failure
        if not result.get("success"):
            return templates.TemplateResponse(
                "cover_letter.html",
                {
                    "request": request,
                    "target_role": position,
                    "cover_letter": None,
                    "error": f"Cover letter generation failed: {result.get('error', 'Unknown error')}. Please try again.",
                    "match_analysis": {},
                    "llm_powered": False,
                    "form_candidate_name": candidate_name,
                    "form_company_name": company_name,
                    "form_position": position,
                    "form_job_description": job_description
                }
            )
        
        # Store for PDF download in user's session
        set_session_data(request, "cover_letter_data", result)
        
        return templates.TemplateResponse(
            "cover_letter.html",
            {
                "request": request,
                "target_role": position,
                "cover_letter": result.get("cover_letter", ""),
                "match_analysis": result.get("match_analysis", {}),
                "llm_powered": result.get("llm_powered", False),
                "company": company_name,
                "position": position,
                "candidate_name": candidate_name,
                "error": None
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "cover_letter.html",
            {
                "request": request,
                "target_role": position,
                "cover_letter": None,
                "error": f"An error occurred: {str(e)}. Please try again.",
                "match_analysis": {},
                "llm_powered": False,
                "form_candidate_name": candidate_name,
                "form_company_name": company_name,
                "form_position": position,
                "form_job_description": job_description
            }
        )


@app.get("/download-cover-letter")
async def download_cover_letter(request: Request):
    """Download cover letter as PDF."""
    cover_letter_data = get_session_data(request, "cover_letter_data")
    
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


@app.post("/api/feedback")
async def submit_feedback(request: Request):
    """Save user feedback to an Excel-compatible CSV file."""
    try:
        data = await request.json()
        name = data.get("name", "Anonymous")
        email = data.get("email", "N/A")
        rating = data.get("rating", 0)
        comment = data.get("comment", "")
        role = get_session_data(request, "role", "N/A")
        
        file_exists = FEEDBACK_FILE.exists()
        
        # Append data to CSV
        with open(FEEDBACK_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header if NEW file
            if not file_exists:
                writer.writerow(["Timestamp", "Name", "Email", "Rating", "Feedback", "Target Role"])
            
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                name,
                email,
                rating,
                comment,
                role
            ])
            
        return JSONResponse({
            "success": True, 
            "message": "Thank you for sharing your thoughts! ❤️ We'll use your suggestions to keep improving Career Copilot."
        })
    except Exception as e:
        print(f"[Error] Feedback saving failed: {e}")
        return JSONResponse({"error": "Failed to save feedback"}, status_code=500)


@app.get("/export-feedback-csv")
async def export_feedback():
    """Download the feedback CSV file (Admin only)."""
    if not FEEDBACK_FILE.exists():
        return JSONResponse({"error": "No feedback collected yet"}, status_code=404)
        
    return Response(
        content=FEEDBACK_FILE.read_text(encoding="utf-8"),
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="career_copilot_feedback.csv"'
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
