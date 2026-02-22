"""
Cover Letter Generator
Uses LLaMA 3.3 + Embeddings for personalized cover letters with JD match analysis
"""

from typing import Dict, Any


def generate_cover_letter(resume_text: str, job_description: str, 
                          company_name: str, position: str,
                          candidate_name: str = "Candidate") -> Dict[str, Any]:
    """
    Generate a personalized cover letter.
    Uses LLaMA 3.3 via Groq, falls back to demo mode if unavailable.
    """
    
    # Try LLaMA + Embeddings (best quality)
    from api_key_pool import get_api_pool
    has_key = get_api_pool().has_available_key()
    if has_key:
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
    
    # Fallback - demo mode
    return generate_demo_cover_letter(resume_text, job_description, 
                                       company_name, position, candidate_name)


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
        "match_analysis": {},
        "company": company_name,
        "position": position,
        "candidate_name": candidate_name,
        "demo_mode": True
    }
