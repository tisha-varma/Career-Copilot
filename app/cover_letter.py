"""
Cover Letter Generator
Uses LLaMA 3.1 + BGE Embeddings for accurate, personalized cover letters
"""

import os
from typing import Dict, Any

# Try LLaMA first, fallback to Gemini
def generate_cover_letter(resume_text: str, job_description: str, 
                          company_name: str, position: str,
                          candidate_name: str = "Candidate") -> Dict[str, Any]:
    """
    Generate a personalized cover letter.
    Uses LLaMA 3.1 via Groq if available, otherwise falls back to Gemini.
    """
    
    # Try LLaMA + Embeddings first (best quality)
    if os.environ.get("GROQ_API_KEY"):
        try:
            from llama_analyzer import generate_cover_letter_llama
            result = generate_cover_letter_llama(
                resume_text=resume_text,
                job_description=job_description,
                company_name=company_name,
                position=position,
                candidate_name=candidate_name
            )
            if result.get("success"):
                return result
        except Exception as e:
            print(f"LLaMA cover letter failed: {e}")
    
    # Fallback to Gemini
    if os.environ.get("GEMINI_API_KEY"):
        try:
            return generate_cover_letter_gemini(
                resume_text=resume_text,
                job_description=job_description,
                company_name=company_name,
                position=position,
                candidate_name=candidate_name
            )
        except Exception as e:
            print(f"Gemini cover letter failed: {e}")
    
    # Final fallback - demo mode
    return generate_demo_cover_letter(resume_text, job_description, 
                                       company_name, position, candidate_name)


def generate_cover_letter_gemini(resume_text: str, job_description: str,
                                  company_name: str, position: str,
                                  candidate_name: str) -> Dict[str, Any]:
    """Generate cover letter using Gemini API."""
    import httpx
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise Exception("No Gemini API key")
    
    prompt = f"""Generate a DETAILED cover letter for {candidate_name} applying to {company_name} for {position}.

RESUME:
{resume_text[:5000]}

JOB DESCRIPTION:
{job_description[:2500]}

Write a 4-5 paragraph cover letter that:
1. Opens with enthusiasm for the role
2. Highlights 2-3 SPECIFIC projects by name with technologies
3. Mentions relevant technical skills and experience  
4. References notable achievements
5. Closes with call to action

Use ONLY information from the resume. Mention specific project names and technologies."""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048}
    }
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        
        return {
            "success": True,
            "cover_letter": text.strip(),
            "company": company_name,
            "position": position,
            "candidate_name": candidate_name,
            "llm_model": "gemini-1.5-flash"
        }
    
    raise Exception(f"Gemini API error: {response.status_code}")


def generate_demo_cover_letter(resume_text: str, job_description: str,
                                company_name: str, position: str,
                                candidate_name: str) -> Dict[str, Any]:
    """Fallback cover letter when APIs unavailable."""
    
    # Simple keyword extraction
    resume_lower = resume_text.lower()
    
    skills = []
    for skill in ['python', 'java', 'javascript', 'react', 'machine learning', 'sql', 'aws']:
        if skill in resume_lower:
            skills.append(skill.title())
    
    skills_text = ", ".join(skills[:4]) if skills else "relevant technical skills"
    
    cover_letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {position} position at {company_name}. With my background in {skills_text}, I am excited about the opportunity to contribute to your team.

Throughout my career, I have developed expertise in areas that align closely with this role's requirements. My project experience has equipped me with the skills necessary to make an immediate impact, and I am eager to bring my knowledge to {company_name}.

I am particularly drawn to this opportunity because it allows me to leverage my technical abilities while continuing to grow professionally. I am confident that my combination of skills and enthusiasm makes me a strong candidate for this position.

I would welcome the opportunity to discuss how my experience can contribute to {company_name}'s success. Thank you for considering my application.

Sincerely,
{candidate_name}"""

    return {
        "success": True,
        "cover_letter": cover_letter,
        "company": company_name,
        "position": position,
        "candidate_name": candidate_name,
        "demo_mode": True
    }
