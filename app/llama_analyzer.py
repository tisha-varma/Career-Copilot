"""
LLaMA-Powered Resume Analyzer with BGE Embeddings
Uses Groq API (LLaMA 3.1) + Sentence Transformers (BGE) + ChromaDB for semantic analysis
"""

import os
import json
from typing import Dict, List, Any, Optional
from groq import Groq
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import hashlib


# Initialize embedding model (BGE-Large for high quality)
# Using all-MiniLM-L6-v2 as fallback (faster, still good quality)
_embedding_model = None
_chroma_client = None

def get_embedding_model():
    """Lazy load embedding model."""
    global _embedding_model
    if _embedding_model is None:
        try:
            # Try BGE-Large first (best quality)
            _embedding_model = SentenceTransformer('BAAI/bge-large-en-v1.5')
            print("✓ Loaded BGE-Large embedding model")
        except Exception:
            # Fallback to smaller model
            _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✓ Loaded MiniLM embedding model")
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
    """Get Groq client for LLaMA access."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")
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
    
    # Create embeddings
    embeddings = model.encode(chunks, show_progress_bar=False).tolist()
    
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
    query_embedding = model.encode([query], show_progress_bar=False).tolist()
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    
    return results['documents'][0] if results['documents'] else []


def call_llama(prompt: str, system_prompt: str = None) -> str:
    """Call LLaMA 3.1 via Groq API."""
    client = get_groq_client()
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",  # or "llama-3.1-8b-instant" for faster
        messages=messages,
        temperature=0.7,
        max_tokens=2048
    )
    
    return response.choices[0].message.content


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


def generate_cover_letter_llama(resume_text: str, job_description: str, 
                                 company_name: str, position: str,
                                 candidate_name: str) -> Dict[str, Any]:
    """Generate personalized cover letter using LLaMA + embeddings."""
    
    # Create session ID for embeddings
    session_id = hashlib.md5(resume_text[:100].encode()).hexdigest()
    
    # Create embeddings for semantic search
    collection = create_resume_embeddings(resume_text, session_id)
    
    # Find most relevant resume sections for this job
    relevant_projects = semantic_search(collection, f"projects {job_description[:200]}", 3)
    relevant_skills = semantic_search(collection, f"skills technologies {job_description[:200]}", 3)
    relevant_experience = semantic_search(collection, f"experience work {job_description[:200]}", 3)
    
    # Extract structured info using LLaMA
    resume_info = extract_resume_info_llama(resume_text)
    
    # Build context for cover letter
    context = f"""
CANDIDATE: {candidate_name}

RELEVANT PROJECTS FROM RESUME:
{chr(10).join(relevant_projects)}

RELEVANT SKILLS:
{chr(10).join(relevant_skills)}

RELEVANT EXPERIENCE:
{chr(10).join(relevant_experience)}

EXTRACTED RESUME INFO:
{json.dumps(resume_info, indent=2)}
"""

    system_prompt = """You are an expert cover letter writer. Write compelling, personalized cover letters 
that highlight specific projects, skills, and achievements from the candidate's resume.
Be professional but engaging. Always reference specific details from the resume."""

    prompt = f"""Write a detailed cover letter for {candidate_name} applying to {company_name} for the {position} role.

{context}

JOB DESCRIPTION:
{job_description[:2000]}

Write a 4-5 paragraph cover letter that:
1. Opens with enthusiasm for the {position} role at {company_name}
2. Highlights 2-3 SPECIFIC projects by name with technologies used
3. Mentions relevant technical skills and experience
4. References any notable achievements
5. Closes with a call to action

IMPORTANT:
- Use ONLY information from the resume context above
- Mention specific project names
- Include specific technologies
- Reference specific achievements
- Do NOT use placeholder text

Write the cover letter now:"""

    try:
        cover_letter = call_llama(prompt, system_prompt)
        
        return {
            "success": True,
            "cover_letter": cover_letter.strip(),
            "company": company_name,
            "position": position,
            "candidate_name": candidate_name,
            "resume_info": resume_info,
            "llm_model": "llama-3.1-70b"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "cover_letter": f"Error generating cover letter: {str(e)}",
            "company": company_name,
            "position": position,
            "candidate_name": candidate_name
        }


def generate_interview_questions_llama(resume_text: str, target_role: str,
                                        strengths: List[str] = None,
                                        skill_gaps: Dict = None) -> Dict[str, Any]:
    """Generate personalized interview questions using LLaMA + embeddings."""
    
    # Create session ID for embeddings
    session_id = hashlib.md5(resume_text[:100].encode()).hexdigest()
    
    # Create embeddings
    collection = create_resume_embeddings(resume_text, session_id)
    
    # Extract resume info
    resume_info = extract_resume_info_llama(resume_text)
    
    # Find relevant sections
    relevant_projects = semantic_search(collection, f"projects technical implementation", 4)
    relevant_experience = semantic_search(collection, f"work experience achievements", 3)
    
    system_prompt = """You are an expert technical interviewer. Generate specific, detailed interview questions 
based on the candidate's resume. Questions must reference SPECIFIC projects, technologies, and achievements.
Always respond with valid JSON."""

    prompt = f"""Generate 8 personalized interview questions for a {target_role} candidate.

RESUME INFORMATION:
{json.dumps(resume_info, indent=2)}

RELEVANT PROJECTS:
{chr(10).join(relevant_projects)}

RELEVANT EXPERIENCE:
{chr(10).join(relevant_experience)}

{f"STRENGTHS: {strengths}" if strengths else ""}
{f"SKILL GAPS: {json.dumps(skill_gaps)}" if skill_gaps else ""}

Generate questions that:
1. Ask about SPECIFIC projects by name
2. Probe technical decisions and implementations
3. Explore achievements and metrics
4. Test problem-solving abilities
5. Assess cultural fit

Return a JSON array:
[
  {{
    "question": "Tell me about your [SPECIFIC PROJECT NAME] project. What challenges did you face with [SPECIFIC TECH]?",
    "category": "Project Experience",
    "source": "Based on [project name] from resume",
    "tip": "Discuss technical implementation, challenges, and measurable outcomes"
  }}
]

Generate 8 questions covering: Projects (3), Technical Skills (2), Experience (2), Growth (1)."""

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
        
        questions = json.loads(response.strip())
        
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
            "llm_model": "llama-3.1-70b"
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
