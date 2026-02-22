"""
Resume Analyzer for Interview Questions
Uses LLaMA 3.3 + BGE Embeddings for accurate question generation
"""

from typing import Dict, List, Any


def get_interview_questions_with_analysis(resume_text: str, target_role: str,
                                           strengths: List[str] = None,
                                           skill_gaps: Dict = None) -> Dict[str, Any]:
    """
    Get personalized interview questions based on resume analysis.
    Uses LLaMA 3.3 via Groq, falls back to demo questions if unavailable.
    """
    
    # Try LLaMA + Embeddings (best quality)
    from api_key_pool import get_api_pool
    has_key = get_api_pool().has_available_key()
    if has_key:
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
    
    # Fallback to demo questions
    return generate_demo_questions(resume_text, target_role, strengths, skill_gaps)


def generate_demo_questions(resume_text: str, target_role: str,
                            strengths: List[str], skill_gaps: Dict) -> Dict[str, Any]:
    """Fallback questions when APIs unavailable."""
    
    questions = [
        {
            "question": f"Tell me about your most impactful project. What technologies did you use?",
            "category": "Project Deep-Dive",
            "source": "General project inquiry",
            "project_context": "Unable to analyze resume - please describe your top project",
            "tip": "Describe the project scope, your role, technologies, and measurable outcomes."
        },
        {
            "question": f"What experience do you have that's most relevant to the {target_role} role?",
            "category": "Role Fit",
            "source": f"Assessing fit for {target_role}",
            "project_context": f"Connecting your background to {target_role} requirements",
            "tip": "Connect your past experience directly to the job requirements."
        },
        {
            "question": "Describe a technical challenge you faced and how you solved it.",
            "category": "Challenges & Growth",
            "source": "Technical assessment",
            "project_context": "Evaluating problem-solving approach",
            "tip": "Use the STAR method: Situation, Task, Action, Result."
        },
        {
            "question": "What's a technology you recently learned? How did you approach learning it?",
            "category": "Challenges & Growth",
            "source": "Learning ability assessment",
            "project_context": "Assessing growth mindset and learning ability",
            "tip": "Show your learning process and how you apply new knowledge."
        }
    ]
    
    return {
        "resume_analysis": {"technologies": [], "projects": [], "companies": [], "key_achievements": []},
        "personalized_questions": questions,
        "llm_powered": False,
        "demo_mode": True
    }
