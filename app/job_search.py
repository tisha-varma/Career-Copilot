"""
Job Search Module
Generate job search URLs and AI-powered personalized job search strategy
"""

import os
import json
import urllib.parse
from typing import Dict, List, Any


def get_job_search_urls(target_role: str, skills: list = None) -> dict:
    """
    Generate job search URLs for major job platforms.
    """
    # Clean role name for URL
    role_encoded = urllib.parse.quote(target_role)
    
    # Build skill keywords
    skill_keywords = ""
    if skills:
        top_skills = skills[:3] if len(skills) > 3 else skills
        skill_keywords = " ".join(top_skills)
        skill_encoded = urllib.parse.quote(skill_keywords)
    else:
        skill_encoded = role_encoded
    
    return {
        "linkedin": {
            "name": "LinkedIn Jobs",
            "url": f"https://www.linkedin.com/jobs/search/?keywords={role_encoded}",
            "icon": "linkedin",
            "color": "blue"
        },
        "indeed": {
            "name": "Indeed",
            "url": f"https://www.indeed.com/jobs?q={role_encoded}",
            "icon": "briefcase",
            "color": "indigo"
        },
        "google": {
            "name": "Google Jobs",
            "url": f"https://www.google.com/search?q={role_encoded}+jobs&ibp=htl;jobs",
            "icon": "search",
            "color": "red"
        },
        "glassdoor": {
            "name": "Glassdoor",
            "url": f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={role_encoded}",
            "icon": "door",
            "color": "green"
        },
        "naukri": {
            "name": "Naukri",
            "url": f"https://www.naukri.com/{target_role.lower().replace(' ', '-')}-jobs",
            "icon": "briefcase",
            "color": "blue"
        }
    }


def get_job_tips(target_role: str) -> list:
    """
    Get job search tips for the target role.
    """
    tips = {
        "Frontend Developer": [
            "Highlight React/Vue/Angular projects in your portfolio",
            "Include GitHub profile with active contributions",
            "Mention responsive design and accessibility experience"
        ],
        "Backend Developer": [
            "Showcase API design and database experience",
            "Mention scalability and performance optimizations",
            "Include cloud platform experience (AWS/GCP/Azure)"
        ],
        "Data Analyst": [
            "Highlight SQL and visualization tool proficiency",
            "Include data storytelling examples",
            "Mention business impact of your analyses"
        ],
        "Full Stack Developer": [
            "Show end-to-end project experience",
            "Highlight both frontend and backend technologies",
            "Include deployment and DevOps experience"
        ],
        "Machine Learning Engineer": [
            "Showcase ML projects with measurable results",
            "Mention production ML system experience",
            "Include research papers or Kaggle rankings"
        ],
        "DevOps Engineer": [
            "Highlight CI/CD pipeline experience",
            "Mention infrastructure-as-code tools",
            "Include monitoring and incident response experience"
        ],
        "Product Manager": [
            "Showcase product launches and metrics",
            "Highlight cross-functional collaboration",
            "Include user research experience"
        ],
        "UX Designer": [
            "Include portfolio with case studies",
            "Show user research methodology",
            "Mention design system experience"
        ]
    }
    
    default_tips = [
        "Tailor your resume for each application",
        "Research the company before applying",
        "Follow up after submitting your application"
    ]
    
    return tips.get(target_role, default_tips)


def generate_job_strategy(resume_text: str, target_role: str, 
                          strengths: List[str] = None,
                          skill_gaps: Dict = None) -> Dict[str, Any]:
    """
    Use LLaMA to generate a personalized job search strategy based on the candidate's resume.
    """
    from api_key_pool import get_api_pool
    pool = get_api_pool()
    api_key = pool.get_key()
    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return get_demo_strategy(target_role, strengths)
    
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        
        system_prompt = """You are an expert career coach and job search strategist. 
Analyze the candidate's resume and provide highly personalized job search advice.
Always respond with valid JSON only. No markdown formatting."""

        prompt = f"""Based on this resume, create a personalized job search strategy for a {target_role} role.

RESUME:
{resume_text[:4000]}

{f"STRENGTHS: {strengths}" if strengths else ""}
{f"SKILL GAPS: {json.dumps(skill_gaps)}" if skill_gaps else ""}

Return a JSON object with this EXACT structure:
{{
    "alternative_titles": [
        "List 5-6 alternative job titles this candidate should also search for based on their skills (e.g., if targeting Frontend Developer, also suggest UI Engineer, React Developer, etc.)"
    ],
    "elevator_pitch": "A 2-3 sentence personalized elevator pitch this candidate can use in cover letters and networking, referencing their SPECIFIC projects and skills from the resume",
    "top_selling_points": [
        {{
            "point": "A specific selling point from their resume (reference actual projects/skills)",
            "how_to_use": "How to present this in applications/interviews"
        }}
    ],
    "target_companies": [
        {{
            "type": "Type of company (e.g., 'AI Startups', 'Big Tech', 'Fintech')",
            "why": "Why this type of company would value this candidate's specific background",
            "examples": "2-3 example companies"
        }}
    ],
    "resume_keywords": ["List 8-10 keywords from their resume that match common job posting requirements for {target_role}"],
    "networking_tips": [
        "3 specific networking suggestions based on their background and target role"
    ],
    "application_strategy": {{
        "customize_for": "What aspect of their resume to customize for each application",
        "highlight_project": "Which project from their resume to lead with and why",
        "address_gaps": "How to address their skill gaps positively in applications"
    }}
}}

Make everything SPECIFIC to this candidate's actual resume content. Do NOT give generic advice."""

        print("Job Strategy: Generating personalized advice (LLaMA)...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2048
        )
        
        text = response.choices[0].message.content.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        strategy = json.loads(text.strip())
        strategy["llm_powered"] = True
        print("✓ Job strategy generated (powered by LLaMA 3.3)")
        return strategy
        
    except Exception as e:
        print(f"Job strategy generation failed: {e}")
        return get_demo_strategy(target_role, strengths)


def get_demo_strategy(target_role: str, strengths: List[str] = None) -> Dict[str, Any]:
    """Fallback strategy when LLM is unavailable."""
    
    role_titles = {
        "Frontend Developer": ["UI Developer", "React Developer", "Web Developer", "JavaScript Developer", "UI Engineer"],
        "Backend Developer": ["Server-Side Developer", "API Developer", "Python Developer", "Java Developer", "Software Engineer"],
        "Full Stack Developer": ["Web Developer", "Software Engineer", "MERN Stack Developer", "Full Stack Engineer", "Application Developer"],
        "Data Analyst": ["Business Analyst", "Data Scientist (Junior)", "Analytics Engineer", "BI Analyst", "Reporting Analyst"],
        "Machine Learning Engineer": ["AI Engineer", "Data Scientist", "Deep Learning Engineer", "NLP Engineer", "ML Ops Engineer"],
        "DevOps Engineer": ["Site Reliability Engineer", "Cloud Engineer", "Platform Engineer", "Infrastructure Engineer", "Build Engineer"],
        "Product Manager": ["Associate PM", "Technical PM", "Product Owner", "Growth PM", "Digital Product Manager"],
        "UX Designer": ["UI/UX Designer", "Product Designer", "Interaction Designer", "Visual Designer", "Design Researcher"]
    }
    
    return {
        "alternative_titles": role_titles.get(target_role, [f"Junior {target_role}", f"Associate {target_role}"]),
        "elevator_pitch": f"I'm a motivated professional targeting {target_role} roles, bringing a combination of technical skills and project experience.",
        "top_selling_points": [],
        "target_companies": [],
        "resume_keywords": [],
        "networking_tips": [
            f"Join {target_role} communities on LinkedIn and Discord",
            "Attend virtual meetups and tech conferences",
            "Connect with people at companies you're interested in"
        ],
        "application_strategy": {
            "customize_for": "Tailor your resume for each specific job posting",
            "highlight_project": "Lead with your most relevant project",
            "address_gaps": "Frame skill gaps as areas of active learning"
        },
        "llm_powered": False,
        "demo_mode": True
    }
