"""
Resume Analyzer for Interview Questions
Uses LLaMA 3.1 + BGE Embeddings for accurate question generation
"""

import os
from typing import Dict, List, Any


def get_interview_questions_with_analysis(resume_text: str, target_role: str,
                                           strengths: List[str] = None,
                                           skill_gaps: Dict = None) -> Dict[str, Any]:
    """
    Get personalized interview questions based on resume analysis.
    Uses LLaMA 3.1 via Groq if available, otherwise falls back to Gemini.
    """
    
    # Try LLaMA + Embeddings first (best quality)
    if os.environ.get("GROQ_API_KEY"):
        try:
            from llama_analyzer import generate_interview_questions_llama
            result = generate_interview_questions_llama(
                resume_text=resume_text,
                target_role=target_role,
                strengths=strengths,
                skill_gaps=skill_gaps
            )
            if result.get("llm_powered"):
                return result
        except Exception as e:
            print(f"LLaMA questions failed: {e}")
    
    # Fallback to Gemini
    if os.environ.get("GEMINI_API_KEY"):
        try:
            return generate_questions_gemini(resume_text, target_role, strengths, skill_gaps)
        except Exception as e:
            print(f"Gemini questions failed: {e}")
    
    # Final fallback
    return generate_demo_questions(resume_text, target_role, strengths, skill_gaps)


def generate_questions_gemini(resume_text: str, target_role: str,
                               strengths: List[str], skill_gaps: Dict) -> Dict[str, Any]:
    """Generate interview questions using Gemini API."""
    import httpx
    import json
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise Exception("No Gemini API key")
    
    prompt = f"""Generate 8 personalized interview questions for a {target_role} candidate.

RESUME:
{resume_text[:4000]}

Generate questions that:
1. Ask about SPECIFIC projects by name from the resume
2. Probe technical decisions and implementations
3. Explore achievements and metrics
4. Test problem-solving abilities

Return a JSON array:
[
  {{
    "question": "Tell me about your [PROJECT NAME] project. What challenges did you face?",
    "category": "Project Experience",
    "source": "Based on [project] from resume",
    "tip": "Discuss technical implementation and outcomes"
  }}
]

Generate 8 specific questions based on the resume content."""

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
        
        # Parse JSON
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        questions = json.loads(text.strip())
        
        return {
            "resume_analysis": {"technologies": [], "projects": [], "companies": [], "key_achievements": []},
            "personalized_questions": questions if isinstance(questions, list) else [],
            "llm_powered": True,
            "llm_model": "gemini-1.5-flash"
        }
    
    raise Exception(f"Gemini API error: {response.status_code}")


def generate_demo_questions(resume_text: str, target_role: str,
                            strengths: List[str], skill_gaps: Dict) -> Dict[str, Any]:
    """Fallback questions when APIs unavailable."""
    
    questions = [
        {
            "question": f"Tell me about your most impactful project. What technologies did you use?",
            "category": "Project Experience",
            "source": "General project inquiry",
            "tip": "Describe the project scope, your role, technologies, and measurable outcomes."
        },
        {
            "question": f"What experience do you have that's most relevant to the {target_role} role?",
            "category": "Role Fit",
            "source": f"Assessing fit for {target_role}",
            "tip": "Connect your past experience directly to the job requirements."
        },
        {
            "question": "Describe a technical challenge you faced and how you solved it.",
            "category": "Problem Solving",
            "source": "Technical assessment",
            "tip": "Use the STAR method: Situation, Task, Action, Result."
        },
        {
            "question": "What's a technology you recently learned? How did you approach learning it?",
            "category": "Growth Mindset",
            "source": "Learning ability assessment",
            "tip": "Show your learning process and how you apply new knowledge."
        }
    ]
    
    return {
        "resume_analysis": {"technologies": [], "projects": [], "companies": [], "key_achievements": []},
        "personalized_questions": questions,
        "llm_powered": False,
        "demo_mode": True
    }
