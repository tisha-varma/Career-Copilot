"""
Agent Module
Orchestrates the agentic resume analysis using Groq API (LLaMA 3.1)
Includes demo mode fallback when API is unavailable
"""

import os
import json
from groq import Groq
from prompts import (
    SYSTEM_PROMPT,
    PROMPT_RESUME_UNDERSTANDING,
    PROMPT_ROLE_FIT_ANALYSIS,
    PROMPT_LEARNING_ROADMAP,
    PROMPT_REFLECTION
)
from api_key_pool import get_api_pool


# Demo mode flag - set to True if API fails
DEMO_MODE = False


def get_groq_client(api_key: str = None):
    """Get Groq client. Uses provided key or fetches from pool."""
    if not api_key:
        pool = get_api_pool()
        api_key = pool.get_key()
        if not api_key:
            raise ValueError("No API keys available (all rate-limited)")
    return Groq(api_key=api_key)


def parse_json_response(response_text: str) -> dict:
    """Parse JSON from LLM response, handling potential markdown formatting."""
    text = response_text.strip()
    
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    
    if text.endswith("```"):
        text = text[:-3]
    
    return json.loads(text.strip())


def call_llm(prompt: str) -> str:
    """
    Call LLaMA 3.3 via Groq API with automatic key rotation.
    Retries with different keys on rate limit errors.
    """
    pool = get_api_pool()
    last_error = None
    
    # Try up to pool.total_keys times (one attempt per key)
    for attempt in range(max(pool.total_keys, 1)):
        api_key = pool.get_key()
        if not api_key:
            break
        
        try:
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2048
            )
            pool.mark_success(api_key)
            return response.choices[0].message.content
            
        except Exception as e:
            last_error = e
            error_msg = str(e).lower()
            
            if "rate_limit" in error_msg or "429" in error_msg:
                pool.mark_rate_limited(api_key, cooldown_seconds=60)
                print(f"[LLM] Key ...{api_key[-6:]} rate-limited, trying next key...")
                continue
            else:
                # Non-rate-limit error, don't retry
                raise
    
    raise Exception(f"All API keys exhausted. Last error: {last_error}")


def get_demo_analysis(resume_text: str, target_role: str) -> dict:
    """Generate a demo analysis based on simple keyword matching."""
    
    resume_lower = resume_text.lower()
    
    # Extract skills by looking for common tech keywords
    all_skills = [
        "python", "javascript", "react", "node.js", "sql", "html", "css",
        "java", "c++", "git", "docker", "aws", "azure", "machine learning",
        "data analysis", "excel", "tableau", "power bi", "pandas", "numpy",
        "tensorflow", "pytorch", "api", "rest", "mongodb", "postgresql",
        "agile", "scrum", "leadership", "communication", "problem solving"
    ]
    
    found_skills = [skill for skill in all_skills if skill in resume_lower]
    
    # Role-specific requirements
    role_requirements = {
        "Frontend Developer": {
            "core": ["react", "javascript", "html", "css", "typescript", "vue.js"],
            "supporting": ["git", "testing", "responsive design", "api integration"]
        },
        "Data Analyst": {
            "core": ["sql", "python", "excel", "data visualization", "statistics"],
            "supporting": ["tableau", "power bi", "pandas", "machine learning basics"]
        },
        "Backend Developer": {
            "core": ["python", "java", "sql", "api", "database design"],
            "supporting": ["docker", "aws", "microservices", "security"]
        },
        "Full Stack Developer": {
            "core": ["javascript", "react", "node.js", "sql", "api"],
            "supporting": ["docker", "git", "cloud services", "devops"]
        },
        "Machine Learning Engineer": {
            "core": ["python", "machine learning", "tensorflow", "pandas"],
            "supporting": ["docker", "aws", "mlops", "statistics"]
        },
        "DevOps Engineer": {
            "core": ["docker", "kubernetes", "aws", "ci/cd", "linux"],
            "supporting": ["python", "terraform", "monitoring", "security"]
        },
        "Product Manager": {
            "core": ["product strategy", "user research", "roadmapping", "agile"],
            "supporting": ["sql", "analytics", "communication", "leadership"]
        },
        "UX Designer": {
            "core": ["figma", "user research", "wireframing", "prototyping"],
            "supporting": ["html", "css", "usability testing", "design systems"]
        }
    }
    
    role_reqs = role_requirements.get(target_role, role_requirements["Frontend Developer"])
    
    # Calculate role fit score
    core_match = len([s for s in role_reqs["core"] if s in resume_lower])
    supporting_match = len([s for s in role_reqs["supporting"] if s in resume_lower])
    
    total_core = len(role_reqs["core"])
    total_supporting = len(role_reqs["supporting"])
    
    score = int(((core_match / total_core) * 70 + (supporting_match / total_supporting) * 30))
    score = max(25, min(95, score + 20))  # Normalize between 25-95
    
    # Find missing skills
    missing_core = [s for s in role_reqs["core"] if s not in resume_lower]
    missing_supporting = [s for s in role_reqs["supporting"] if s not in resume_lower]
    
    # Generate strengths based on found skills
    strengths = []
    if found_skills:
        strengths.append(f"Technical proficiency in {', '.join(found_skills[:3])}")
    if "leadership" in resume_lower or "led" in resume_lower or "managed" in resume_lower:
        strengths.append("Leadership and team management experience")
    if "project" in resume_lower:
        strengths.append("Project delivery experience")
    if len(found_skills) > 5:
        strengths.append("Diverse technical skill set")
    if "agile" in resume_lower or "scrum" in resume_lower:
        strengths.append("Agile methodology experience")
    
    if not strengths:
        strengths = ["Foundational knowledge present", "Enthusiasm for learning"]
    
    # Generate roadmap
    roadmap = []
    for i, skill in enumerate(missing_core[:3]):
        roadmap.append({
            "skill": skill.title(),
            "priority": "High",
            "estimated_time": f"{(i+1)*2} weeks",
            "expected_outcome": f"Become proficient in {skill} for {target_role} role"
        })
    
    for i, skill in enumerate(missing_supporting[:2]):
        roadmap.append({
            "skill": skill.title(),
            "priority": "Medium",
            "estimated_time": f"{(i+1)} week",
            "expected_outcome": f"Add {skill} as a supporting skill"
        })
    
    if not roadmap:
        roadmap = [{
            "skill": "Advanced " + (found_skills[0] if found_skills else "Programming"),
            "priority": "Medium",
            "estimated_time": "3 weeks",
            "expected_outcome": "Deepen existing expertise"
        }]
    
    return {
        "role_fit_score": score,
        "strengths": strengths[:4],
        "skill_gaps": {
            "core": missing_core[:4],
            "supporting": missing_supporting[:3]
        },
        "roadmap": roadmap,
        "analysis_notes": f"Based on resume analysis, you show {score}% alignment with the {target_role} role. Focus on the identified skill gaps to improve your candidacy.",
        "reflection": {
            "status": "sufficient",
            "reason": f"This roadmap addresses the key gaps for {target_role}. Following it will significantly improve your role fit."
        },
        "target_role": target_role,
        "demo_mode": True
    }


async def run_agent(resume_text: str, target_role: str) -> dict:
    """Run the agentic analysis loop using Groq/LLaMA."""
    
    try:
        # Step 1: Understand the resume
        print("Agent Step 1: Resume Understanding (LLaMA 3.1)...")
        prompt1 = PROMPT_RESUME_UNDERSTANDING.format(resume_text=resume_text)
        response1 = call_llm(prompt1)
        resume_understanding = parse_json_response(response1)
        
        # Step 2: Analyze role fit
        print("Agent Step 2: Role Fit Analysis (LLaMA 3.1)...")
        prompt2 = PROMPT_ROLE_FIT_ANALYSIS.format(
            skills=", ".join(resume_understanding.get("skills", [])),
            education_level=resume_understanding.get("education_level", "Unknown"),
            experience_level=resume_understanding.get("experience_level", "Unknown"),
            strengths=", ".join(resume_understanding.get("strengths", [])),
            target_role=target_role
        )
        response2 = call_llm(prompt2)
        role_fit_analysis = parse_json_response(response2)
        
        # Step 3: Generate learning roadmap
        print("Agent Step 3: Learning Roadmap (LLaMA 3.1)...")
        prompt3 = PROMPT_LEARNING_ROADMAP.format(
            missing_core_skills=", ".join(role_fit_analysis.get("missing_core_skills", [])),
            missing_supporting_skills=", ".join(role_fit_analysis.get("missing_supporting_skills", [])),
            target_role=target_role
        )
        response3 = call_llm(prompt3)
        learning_roadmap = parse_json_response(response3)
        
        # Step 4: Reflection
        print("Agent Step 4: Reflection (LLaMA 3.1)...")
        prompt4 = PROMPT_REFLECTION.format(
            role_fit_score=role_fit_analysis.get("role_fit_score", 0),
            roadmap_count=len(learning_roadmap.get("roadmap", [])),
            target_role=target_role
        )
        response4 = call_llm(prompt4)
        reflection = parse_json_response(response4)
        
        print("✓ Agent analysis complete (powered by LLaMA 3.1 via Groq)")
        
        # Combine all results
        return {
            "role_fit_score": role_fit_analysis.get("role_fit_score", 0),
            "strengths": resume_understanding.get("strengths", []),
            "skill_gaps": {
                "core": role_fit_analysis.get("missing_core_skills", []),
                "supporting": role_fit_analysis.get("missing_supporting_skills", [])
            },
            "roadmap": learning_roadmap.get("roadmap", []),
            "analysis_notes": role_fit_analysis.get("analysis_notes", ""),
            "reflection": reflection,
            "target_role": target_role
        }
        
    except Exception as e:
        # If Groq API fails, use demo mode
        print(f"Groq API failed ({e}), using demo mode...")
        global DEMO_MODE
        DEMO_MODE = True
        return get_demo_analysis(resume_text, target_role)
