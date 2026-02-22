"""
Prompts Module
Contains all Groq/LLaMA prompts for the agentic resume analysis
"""

# System prompt for the career analysis agent
SYSTEM_PROMPT = """You are an autonomous career analysis agent.
Analyze a resume against a target job role.
Identify strengths, skill gaps, and generate a realistic learning roadmap.
Do NOT rewrite the resume.
Do NOT invent experience.
Return clean JSON only."""


# Prompt 1: Resume Understanding
PROMPT_RESUME_UNDERSTANDING = """Analyze the following resume and extract key information.

RESUME:
{resume_text}

Return a JSON object with the following structure (no markdown, just raw JSON):
{{
  "skills": ["list of technical and soft skills found"],
  "education_level": "highest education level (e.g., Bachelor's, Master's, PhD, High School)",
  "experience_level": "entry/junior/mid/senior based on years and roles",
  "strengths": ["key strengths identified from the resume"]
}}"""


# Prompt 2: Role Fit Analysis
PROMPT_ROLE_FIT_ANALYSIS = """Based on the resume summary and target job role, analyze the candidate's fit.

RESUME SUMMARY:
Skills: {skills}
Education: {education_level}
Experience Level: {experience_level}
Strengths: {strengths}

TARGET ROLE: {target_role}

Return a JSON object with the following structure (no markdown, just raw JSON):
{{
  "role_fit_score": <number from 0-100>,
  "missing_core_skills": ["essential skills for this role that are missing"],
  "missing_supporting_skills": ["nice-to-have skills that are missing"],
  "analysis_notes": "brief explanation of the score and fit assessment"
}}"""


# Prompt 3: Learning Roadmap
PROMPT_LEARNING_ROADMAP = """Create a personalized learning roadmap based on the missing skills.

MISSING CORE SKILLS: {missing_core_skills}
MISSING SUPPORTING SKILLS: {missing_supporting_skills}
TARGET ROLE: {target_role}

Return a JSON object with the following structure (no markdown, just raw JSON):
{{
  "roadmap": [
    {{
      "skill": "skill name",
      "priority": "High | Medium | Low",
      "estimated_time": "e.g., 2 weeks, 1 month",
      "expected_outcome": "what the candidate will be able to do after learning this"
    }}
  ]
}}

Order the roadmap by priority (High first, then Medium, then Low).
Include 3-6 items maximum."""


# Prompt 4: Reflection
PROMPT_REFLECTION = """Review the analysis and roadmap to determine if the guidance is sufficient.

ROLE FIT SCORE: {role_fit_score}
LEARNING ROADMAP ITEMS: {roadmap_count}
TARGET ROLE: {target_role}

Return a JSON object with the following structure (no markdown, just raw JSON):
{{
  "status": "sufficient",
  "reason": "brief explanation of why this guidance is enough for the candidate"
}}"""
