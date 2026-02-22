import os
import json
from typing import Dict, List, Any, Optional
from groq import Groq
from fastembed import TextEmbedding
import chromadb
from chromadb.config import Settings
import hashlib


# Initialize embedding model (Fast, lightweight, optimized for CPU)
# Using BGE-Small (excellent quality, very small footprint)
_embedding_model = None
_chroma_client = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        try:
            # fastembed uses ONNX Runtime (much lighter than PyTorch)
            _embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
            print("✓ Loaded fastembed model (BGE-Small)")
        except Exception as e:
            print(f"Error loading embedding model: {e}")
            # Fallback to local default if possible, but fastembed is preferred
            _embedding_model = TextEmbedding()
    return _embedding_model


def get_chroma_client():
    """Get ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            is_persistent=False
        ))
    return _chroma_client


def get_groq_client():
    """Get Groq client using the API key pool."""
    from api_key_pool import get_api_pool
    pool = get_api_pool()
    api_key = pool.get_key()
    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("No API keys available")
    return Groq(api_key=api_key)


def chunk_resume(resume_text: str, chunk_size: int = 500) -> List[str]:
    """Split resume into meaningful chunks for embedding."""
    # Split by double newlines (sections)
    sections = resume_text.split('\n\n')
    
    chunks = []
    current_chunk = ""
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        if len(current_chunk) + len(section) < chunk_size:
            current_chunk += "\n\n" + section if current_chunk else section
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = section
    
    if current_chunk:
        chunks.append(current_chunk)
    
    # Also split by single newlines for granular matching
    for section in sections:
        lines = section.strip().split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 30:  # Meaningful lines only
                chunks.append(line)
    
    return list(set(chunks))  # Remove duplicates


def create_resume_embeddings(resume_text: str, session_id: str) -> chromadb.Collection:
    """Create embeddings for resume chunks and store in ChromaDB."""
    model = get_embedding_model()
    client = get_chroma_client()
    
    # Create unique collection name based on session
    collection_name = f"resume_{session_id[:8]}"
    
    # Delete existing collection if exists
    try:
        client.delete_collection(collection_name)
    except:
        pass
    
    # Create new collection
    collection = client.create_collection(
        name=collection_name,
        metadata={"description": "Resume chunks with embeddings"}
    )
    
    # Chunk the resume
    chunks = chunk_resume(resume_text)
    
    if not chunks:
        return collection
    
    # Create embeddings (fastembed model.embed returns a generator)
    # Convert to list of lists for ChromaDB
    embeddings = [e.tolist() for e in list(model.embed(chunks))]
    
    # Add to collection
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    
    return collection


def semantic_search(collection: chromadb.Collection, query: str, n_results: int = 5) -> List[str]:
    """Search for relevant resume chunks using semantic similarity."""
    model = get_embedding_model()
    # model.embed returns a generator, even for a single query
    query_embeddings = [e.tolist() for e in list(model.embed([query]))]
    
    results = collection.query(
        query_embeddings=query_embeddings,
        n_results=n_results
    )
    
    return results['documents'][0] if results['documents'] else []


def call_llama(prompt: str, system_prompt: str = None) -> str:
    """
    Call LLaMA 3.3 via Groq API with automatic key rotation and retries.
    """
    from api_key_pool import get_api_pool
    pool = get_api_pool()
    last_error = None
    
    # Try once for every key in the pool
    for attempt in range(max(pool.total_keys, 1)):
        api_key = pool.get_key()
        if not api_key:
            # Fallback to env if pool is somehow empty
            api_key = os.environ.get("GROQ_API_KEY")
            if not api_key:
                break
        
        try:
            client = Groq(api_key=api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=2048
            )
            
            pool.mark_success(api_key)
            return response.choices[0].message.content
            
        except Exception as e:
            last_error = e
            error_msg = str(e).lower()
            
            # If it's a rate limit error, mark the key as limited and try the next one
            if "rate_limit" in error_msg or "429" in error_msg:
                pool.mark_rate_limited(api_key, cooldown_seconds=60)
                print(f"[LLaMA] Key ...{api_key[-6:]} rate-limited, rotating...")
                continue
            else:
                # Other errors (auth, validation) shouldn't be retried with same logic
                raise
                
    raise Exception(f"Failed to call LLaMA after trying available keys. Last error: {last_error}")


def extract_resume_info_llama(resume_text: str) -> Dict[str, Any]:
    """Use LLaMA to extract structured information from resume."""
    
    system_prompt = """You are an expert resume parser. Extract structured information from resumes accurately.
Always respond with valid JSON only, no additional text."""

    prompt = f"""Analyze this resume and extract the following information in JSON format:

RESUME:
{resume_text[:4000]}

Return a JSON object with this exact structure:
{{
    "name": "candidate's full name",
    "projects": [
        {{
            "name": "project name",
            "description": "what the project does",
            "technologies": ["tech1", "tech2"],
            "achievements": ["achievement or metric if any"]
        }}
    ],
    "experience": [
        {{
            "role": "job title",
            "company": "company name",
            "duration": "time period",
            "achievements": ["key achievement 1", "key achievement 2"]
        }}
    ],
    "skills": {{
        "programming": ["language1", "language2"],
        "frameworks": ["framework1", "framework2"],
        "ai_ml": ["skill1", "skill2"],
        "tools": ["tool1", "tool2"],
        "databases": ["db1", "db2"]
    }},
    "education": [
        {{
            "degree": "degree name",
            "institution": "school/university",
            "year": "graduation year or period",
            "gpa": "GPA if mentioned"
        }}
    ],
    "achievements": ["award or recognition 1", "award 2"],
    "summary": "A 2-3 sentence summary of the candidate's profile"
}}

Extract ONLY information present in the resume. Do not invent anything."""

    try:
        response = call_llama(prompt, system_prompt)
        
        # Clean response
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        
        return json.loads(response.strip())
        
    except Exception as e:
        print(f"LLaMA extraction error: {e}")
        return {
            "name": "",
            "projects": [],
            "experience": [],
            "skills": {"programming": [], "frameworks": [], "ai_ml": [], "tools": [], "databases": []},
            "education": [],
            "achievements": [],
            "summary": ""
        }


import re

def _format_cover_letter(text: str) -> str:
    """Ensure the cover letter has proper paragraph breaks."""
    if not text:
        return text
    
    # If already has paragraph breaks (2+ newlines), just normalize them
    if '\n\n' in text:
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        return '\n\n'.join(paragraphs)
    
    # If single newlines exist, try splitting on those
    if '\n' in text:
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        # If we get 3+ lines, they're probably paragraphs
        if len(lines) >= 3:
            return '\n\n'.join(lines)
    
    # No newlines at all — need to split intelligently
    # Split after greeting
    text = re.sub(r'(Dear\s+(?:Hiring Manager|[^,]+),)', r'\1\n\n', text)
    # Split before closing
    text = re.sub(r'\s+(Sincerely|Best regards|Regards|Yours truly|Warm regards|Thank you)', r'\n\n\1', text, flags=re.IGNORECASE)
    
    # Now split the body into paragraphs roughly every 3-4 sentences
    parts = text.split('\n\n')
    result = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # If a body paragraph is very long (>500 chars), split it
        if len(part) > 500:
            sentences = re.split(r'(?<=[.!?])\s+', part)
            chunk = []
            chunk_len = 0
            for s in sentences:
                chunk.append(s)
                chunk_len += len(s)
                if chunk_len > 300 and len(chunk) >= 3:
                    result.append(' '.join(chunk))
                    chunk = []
                    chunk_len = 0
            if chunk:
                result.append(' '.join(chunk))
        else:
            result.append(part)
    
    return '\n\n'.join(result)


def generate_cover_letter_llama(resume_text: str, job_description: str, 
                                 company_name: str, position: str,
                                 candidate_name: str) -> Dict[str, Any]:
    """Generate deeply personalized cover letter using LLaMA + embeddings."""
    
    # Create session ID for embeddings
    session_id = hashlib.md5(resume_text[:100].encode()).hexdigest()
    
    # Create embeddings for semantic search
    collection = create_resume_embeddings(resume_text, session_id)
    
    # Semantic search tailored to the job description
    relevant_projects = semantic_search(collection, f"projects {job_description[:300]}", 5)
    relevant_skills = semantic_search(collection, f"skills technologies {job_description[:300]}", 4)
    relevant_experience = semantic_search(collection, f"experience work achievements {job_description[:300]}", 4)
    relevant_impact = semantic_search(collection, f"results impact metrics improved reduced increased", 3)
    
    # Extract structured info using LLaMA
    print("Cover Letter: Extracting resume details (LLaMA)...")
    resume_info = extract_resume_info_llama(resume_text)
    
    # Build rich context
    projects_detail = json.dumps(resume_info.get("projects", []), indent=2)
    experience_detail = json.dumps(resume_info.get("experience", []), indent=2)
    skills_detail = json.dumps(resume_info.get("skills", {}), indent=2)
    achievements = resume_info.get("achievements", [])
    
    system_prompt = """You are an elite cover letter writer who creates cover letters that get interviews.
Your cover letters are HIGHLY SPECIFIC — they reference exact project names, technologies, metrics, 
and achievements from the candidate's resume and precisely map them to job requirements.

You NEVER write generic phrases like "I have relevant experience" — instead you write things like
"My work on the Career Copilot AI project, where I built a FastAPI backend with 4-step agentic LLM workflow, 
directly maps to your need for candidates experienced in building production AI systems."

ALWAYS respond with valid JSON only."""

    prompt = f"""Create a deeply personalized cover letter AND a match analysis for {candidate_name} applying to {company_name} for {position}.

=== CANDIDATE'S PROJECTS ===
{projects_detail}

=== CANDIDATE'S EXPERIENCE ===
{experience_detail}

=== CANDIDATE'S SKILLS ===
{skills_detail}

=== CANDIDATE'S ACHIEVEMENTS ===
{json.dumps(achievements, indent=2)}

=== RELEVANT PROJECT SECTIONS FROM RESUME ===
{chr(10).join(relevant_projects)}

=== RELEVANT SKILLS SECTIONS ===
{chr(10).join(relevant_skills)}

=== RELEVANT EXPERIENCE SECTIONS ===
{chr(10).join(relevant_experience)}

=== IMPACT & METRICS FROM RESUME ===
{chr(10).join(relevant_impact)}

=== JOB DESCRIPTION ===
{job_description[:2500]}

Return a JSON object with this EXACT structure:
{{
    "cover_letter": "The full cover letter text (4-5 paragraphs). Rules:\\n- Paragraph 1: Strong opening mentioning the specific role and company, plus ONE compelling achievement from the resume\\n- Paragraph 2: Reference 2 SPECIFIC projects BY NAME with exact technologies used, explaining how they match the JD requirements\\n- Paragraph 3: Highlight technical skills and another specific project/experience that demonstrates a key JD requirement\\n- Paragraph 4: (Optional) Reference any measurable achievements, metrics, or impact numbers from the resume\\n- Paragraph 5: Confident close with call to action\\n\\nStart with 'Dear Hiring Manager,' and end with 'Sincerely,\\n{candidate_name}'\\nUse ACTUAL project names and technologies from the resume. Never use placeholders.",
    "match_analysis": {{
        "matched_requirements": [
            {{
                "jd_requirement": "A specific requirement from the job description",
                "resume_match": "The specific project, skill, or experience from the resume that matches this",
                "strength": "strong | moderate | partial"
            }}
        ],
        "key_projects_highlighted": [
            {{
                "project_name": "Name of the project from resume",
                "relevance": "Why this project is relevant to the job"
            }}
        ],
        "skills_coverage": {{
            "matched": ["Skills from JD that the candidate has"],
            "missing": ["Skills from JD that the candidate should learn"]
        }}
    }}
}}"""

    try:
        print("Cover Letter: Generating personalized letter (LLaMA)...")
        response = call_llama(prompt, system_prompt)
        
        # Clean response
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        
        result = json.loads(response.strip())
        print("✓ Cover letter generated (powered by LLaMA 3.3)")
        
        # Post-process: ensure proper paragraph formatting
        cover_text = result.get("cover_letter", "").strip()
        cover_text = _format_cover_letter(cover_text)
        
        return {
            "success": True,
            "cover_letter": cover_text,
            "match_analysis": result.get("match_analysis", {}),
            "company": company_name,
            "position": position,
            "candidate_name": candidate_name,
            "resume_info": resume_info,
            "llm_model": "llama-3.3-70b",
            "llm_powered": True
        }
        
    except Exception as e:
        print(f"Cover letter JSON parse failed, trying plain text: {e}")
        # If JSON fails, try generating plain text cover letter
        try:
            plain_prompt = f"""Write a cover letter for {candidate_name} applying to {company_name} for {position}.

RESUME PROJECTS: {projects_detail}
RESUME SKILLS: {skills_detail}
JOB DESCRIPTION: {job_description[:2000]}

Write 4-5 paragraphs referencing SPECIFIC project names and technologies from the resume.
Start with 'Dear Hiring Manager,' and end with 'Sincerely,\\n{candidate_name}'"""
            
            cover_letter = call_llama(plain_prompt, "You are an expert cover letter writer. Be specific — reference actual project names and technologies.")
            
            return {
                "success": True,
                "cover_letter": cover_letter.strip(),
                "match_analysis": {},
                "company": company_name,
                "position": position,
                "candidate_name": candidate_name,
                "llm_model": "llama-3.3-70b",
                "llm_powered": True
            }
        except Exception as e2:
            return {
                "success": False,
                "error": str(e2),
                "cover_letter": f"Error generating cover letter: {str(e2)}",
                "match_analysis": {},
                "company": company_name,
                "position": position,
                "candidate_name": candidate_name
            }


def generate_interview_questions_llama(resume_text: str, target_role: str,
                                        strengths: List[str] = None,
                                        skill_gaps: Dict = None) -> Dict[str, Any]:
    """Generate deeply personalized interview questions using LLaMA + embeddings."""
    
    # Create session ID for embeddings
    session_id = hashlib.md5(resume_text[:100].encode()).hexdigest()
    
    # Create embeddings
    collection = create_resume_embeddings(resume_text, session_id)
    
    # Extract structured resume info using LLaMA
    print("Interview Prep: Extracting resume details (LLaMA)...")
    resume_info = extract_resume_info_llama(resume_text)
    
    # Semantic search for different aspects of the resume
    relevant_projects = semantic_search(collection, "projects technical implementation architecture design", 5)
    relevant_experience = semantic_search(collection, "work experience role achievements impact metrics", 4)
    relevant_tech = semantic_search(collection, "technologies frameworks tools programming languages", 4)
    relevant_challenges = semantic_search(collection, "challenges problems solved improved optimized", 3)
    
    # Build rich project context for the prompt
    projects_detail = json.dumps(resume_info.get("projects", []), indent=2)
    experience_detail = json.dumps(resume_info.get("experience", []), indent=2)
    skills_detail = json.dumps(resume_info.get("skills", {}), indent=2)
    
    system_prompt = """You are a senior technical interviewer at a top tech company. Your job is to generate 
HIGHLY SPECIFIC and DEEPLY PERSONALIZED interview questions based on the candidate's actual resume.

CRITICAL RULES:
- Every question MUST reference a SPECIFIC project name, technology, company, or achievement from the resume
- Questions should probe the candidate's DEPTH of understanding, not surface-level knowledge
- Ask about WHY they made certain technical decisions, not just WHAT they built
- Include questions about trade-offs, challenges faced, and lessons learned
- Reference actual metrics, numbers, or outcomes mentioned in the resume
- NEVER generate generic questions that could apply to any candidate

Always respond with valid JSON only."""

    prompt = f"""Generate 10 deeply personalized interview questions for this candidate applying for a {target_role} role.

=== CANDIDATE'S PROJECTS (with details) ===
{projects_detail}

=== CANDIDATE'S WORK EXPERIENCE ===
{experience_detail}

=== CANDIDATE'S SKILLS ===
{skills_detail}

=== RELEVANT PROJECT DETAILS FROM RESUME ===
{chr(10).join(relevant_projects)}

=== WORK EXPERIENCE HIGHLIGHTS ===
{chr(10).join(relevant_experience)}

=== TECHNOLOGIES MENTIONED ===
{chr(10).join(relevant_tech)}

=== CHALLENGES & ACHIEVEMENTS ===
{chr(10).join(relevant_challenges)}

{f"IDENTIFIED STRENGTHS: {strengths}" if strengths else ""}
{f"SKILL GAPS TO PROBE: {json.dumps(skill_gaps)}" if skill_gaps else ""}

=== QUESTION CATEGORIES (generate exactly this distribution) ===
1. PROJECT DEEP-DIVE (4 questions): Ask about specific projects BY NAME. Probe:
   - "In your [PROJECT NAME] project, you used [TECH]. Why did you choose [TECH] over alternatives like [ALT]?"
   - "Walk me through the architecture of [PROJECT NAME]. How did you handle [SPECIFIC CHALLENGE]?"
   - "You mentioned [SPECIFIC FEATURE] in [PROJECT NAME]. How did you implement that technically?"
   - "What was the most difficult bug or challenge you faced in [PROJECT NAME]?"

2. TECHNICAL ARCHITECTURE (2 questions): Ask about system design decisions:
   - "In [PROJECT], you combined [TECH1] and [TECH2]. How did these components communicate?"
   - "If you had to scale [PROJECT NAME] to 10x users, what would you change?"

3. IMPACT & METRICS (2 questions): Ask about measurable outcomes:
   - "You mentioned [SPECIFIC METRIC/ACHIEVEMENT]. How did you measure that?"
   - "What was the business impact of [PROJECT/FEATURE]?"

4. CHALLENGES & GROWTH (1 question): Ask about learning from difficulties:
   - "What technology in [PROJECT] was new to you? How did you get up to speed?"

5. ROLE FIT (1 question): Connect their experience to the {target_role} role:
   - "How does your experience with [SPECIFIC TECH/PROJECT] prepare you for [ASPECT OF TARGET ROLE]?"

Return a JSON array with exactly 10 questions:
[
  {{
    "question": "The actual personalized question referencing specific resume details",
    "category": "Project Deep-Dive | Technical Architecture | Impact & Metrics | Challenges & Growth | Role Fit",
    "source": "Based on [specific project/experience/achievement] from resume",
    "project_context": "Brief context about what in the resume triggered this question",
    "tip": "Specific advice on how to answer THIS question well, referencing what they should highlight"
  }}
]"""

    try:
        print("Interview Prep: Generating personalized questions (LLaMA)...")
        response = call_llama(prompt, system_prompt)
        
        # Clean response
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        
        questions = json.loads(response.strip())
        print(f"✓ Generated {len(questions) if isinstance(questions, list) else 0} personalized interview questions")
        
        return {
            "resume_analysis": {
                "technologies": resume_info.get("skills", {}).get("programming", []) + 
                               resume_info.get("skills", {}).get("frameworks", []),
                "projects": [p.get("name") for p in resume_info.get("projects", [])],
                "companies": [e.get("company") for e in resume_info.get("experience", [])],
                "key_achievements": resume_info.get("achievements", [])
            },
            "personalized_questions": questions if isinstance(questions, list) else [],
            "llm_powered": True,
            "llm_model": "llama-3.3-70b"
        }
        
    except Exception as e:
        print(f"LLaMA questions error: {e}")
        return {
            "resume_analysis": {"technologies": [], "projects": [], "companies": [], "key_achievements": []},
            "personalized_questions": [],
            "llm_powered": False,
            "error": str(e)
        }


# Main function to get interview questions (called by main.py)
def get_interview_questions_with_analysis(resume_text: str, target_role: str,
                                           strengths: List[str] = None,
                                           skill_gaps: Dict = None) -> Dict[str, Any]:
    """Main entry point for interview question generation."""
    try:
        return generate_interview_questions_llama(resume_text, target_role, strengths, skill_gaps)
    except Exception as e:
        # Fallback if Groq API fails
        print(f"Falling back to basic mode: {e}")
        return {
            "resume_analysis": {"technologies": [], "projects": [], "companies": [], "key_achievements": []},
            "personalized_questions": [],
            "llm_powered": False,
            "error": str(e)
        }
