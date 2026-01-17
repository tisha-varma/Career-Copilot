"""
Structured Resume Extractor
Extracts detailed structured information from resume text
for accurate cover letter generation and interview questions
"""

import re
from typing import Dict, List, Any


def extract_structured_resume_data(resume_text: str) -> Dict[str, Any]:
    """
    Extract structured data from resume text.
    Returns a comprehensive dict with all resume sections.
    """
    
    resume_lower = resume_text.lower()
    
    # Initialize result structure
    data = {
        "name": "",
        "projects": [],
        "experience": [],
        "skills": {
            "programming": [],
            "ai_ml": [],
            "frameworks": [],
            "tools": [],
            "databases": []
        },
        "education": [],
        "achievements": [],
        "training": []
    }
    
    # Extract name (usually first line or prominent text)
    lines = resume_text.strip().split('\n')
    for line in lines[:5]:
        line = line.strip()
        # Name is usually short, capitalized, no special chars
        if line and len(line) < 50 and line.isupper() or (len(line.split()) <= 4 and line[0].isupper()):
            if not any(skip in line.lower() for skip in ['resume', 'cv', 'curriculum', '@', 'http', 'phone', 'email']):
                data["name"] = line.title()
                break
    
    # Extract projects
    data["projects"] = extract_projects(resume_text)
    
    # Extract experience
    data["experience"] = extract_experience(resume_text)
    
    # Extract skills
    data["skills"] = extract_skills(resume_text)
    
    # Extract education
    data["education"] = extract_education(resume_text)
    
    # Extract achievements
    data["achievements"] = extract_achievements(resume_text)
    
    # Extract training
    data["training"] = extract_training(resume_text)
    
    return data


def extract_projects(resume_text: str) -> List[Dict[str, str]]:
    """Extract project details with name, tech stack, and description."""
    projects = []
    
    # Skip patterns - these are NOT projects
    skip_patterns = [
        'experience', 'education', 'skills', 'intern', 'bachelor', 'diploma',
        'master', 'college', 'university', 'technical', 'programming', 'achievement',
        'training', 'certification', 'finalist', 'pvt', 'ltd', 'services',
        'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
        '2020', '2021', '2022', '2023', '2024', '2025', '2026', '2027'
    ]
    
    lines = resume_text.split('\n')
    current_project = None
    in_project_section = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Detect project section start
        if 'project' in line.lower() and len(line) < 30:
            in_project_section = True
            continue
        
        # Detect section end
        if in_project_section and any(s in line.lower() for s in ['experience', 'technical skills', 'education', 'achievements']):
            in_project_section = False
            current_project = None
            continue
        
        # Look for Tech: line to get tech stack
        if 'Tech:' in line or 'Technologies:' in line:
            tech_match = re.search(r'Tech(?:nologies)?:\s*(.+)', line, re.IGNORECASE)
            if tech_match and current_project:
                current_project['tech'] = tech_match.group(1).strip()
            continue
        
        # Detect project names (Title Case with – or —, NOT matching skip patterns)
        if ('–' in line or '—' in line) and in_project_section:
            parts = re.split(r'[–—]', line, 1)
            if len(parts) >= 1:
                project_name = parts[0].strip()
                description = parts[1].strip() if len(parts) > 1 else ""
                
                # Skip if matches skip patterns
                if any(skip in project_name.lower() for skip in skip_patterns):
                    continue
                
                # Skip if project name is too short or too long
                if len(project_name) < 3 or len(project_name) > 60:
                    continue
                
                # Valid project found
                current_project = {
                    'name': project_name,
                    'description': description,
                    'tech': '',
                    'details': []
                }
                projects.append(current_project)
        
        # Also try projects section without dashes (just look for lines starting with capital, followed by Tech:)
        elif in_project_section and i + 1 < len(lines):
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
            if 'Tech:' in next_line and not any(skip in line.lower() for skip in skip_patterns):
                if len(line) > 5 and len(line) < 80:
                    current_project = {
                        'name': line,
                        'description': '',
                        'tech': '',
                        'details': []
                    }
                    projects.append(current_project)
        
        # Collect bullet points for current project
        elif current_project and (line.startswith('•') or line.startswith('-') or line.startswith('▪')):
            detail = line.lstrip('•-▪ ').strip()
            if detail and len(detail) > 15:
                current_project['details'].append(detail)
        
        # Collect action verb lines as details
        elif current_project and any(verb in line.lower() for verb in ['developed', 'built', 'implemented', 'designed', 'created', 'achieved', 'reduced', 'improved', 'addressed']):
            if len(line) > 20 and len(line) < 200:
                current_project['details'].append(line)
    
    # Remove duplicates and filter
    seen_names = set()
    unique_projects = []
    for proj in projects:
        name = proj['name'].lower()
        if name not in seen_names and len(proj['name']) > 3:
            seen_names.add(name)
            unique_projects.append(proj)
    
    return unique_projects[:4]  # Max 4 projects


def extract_experience(resume_text: str) -> List[Dict[str, str]]:
    """Extract work experience with company, role, duration, and achievements."""
    experiences = []
    
    lines = resume_text.split('\n')
    current_exp = None
    in_experience_section = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Detect experience section
        if 'experience' in line.lower() and len(line) < 30:
            in_experience_section = True
            continue
        
        # Detect end of experience section
        if in_experience_section and any(section in line.lower() for section in ['skills', 'education', 'projects', 'achievements']):
            in_experience_section = False
        
        if in_experience_section:
            # Look for role titles (usually contain 'intern', 'engineer', 'developer', etc.)
            if any(role in line.lower() for role in ['intern', 'engineer', 'developer', 'analyst', 'manager', 'associate']):
                current_exp = {
                    'role': line,
                    'company': '',
                    'duration': '',
                    'achievements': []
                }
                experiences.append(current_exp)
            
            # Look for company names (often followed by dates)
            elif current_exp and '|' in line:
                parts = line.split('|')
                current_exp['company'] = parts[0].strip()
                if len(parts) > 1:
                    current_exp['duration'] = parts[1].strip()
            
            # Collect achievements
            elif current_exp and (line.startswith('•') or line.startswith('-') or 
                                  any(verb in line.lower() for verb in ['built', 'developed', 'contributed', 'implemented'])):
                detail = line.lstrip('•-▪ ').strip()
                if detail and len(detail) > 10:
                    current_exp['achievements'].append(detail)
    
    return experiences


def extract_skills(resume_text: str) -> Dict[str, List[str]]:
    """Extract categorized technical skills."""
    skills = {
        "programming": [],
        "ai_ml": [],
        "frameworks": [],
        "tools": [],
        "databases": []
    }
    
    resume_lower = resume_text.lower()
    
    # Programming languages - with word boundaries to avoid false matches
    prog_langs = [
        (r'\bpython\b', 'Python'),
        (r'\bjava\b(?!script)', 'Java'),  # java but not javascript
        (r'\bjavascript\b', 'JavaScript'),
        (r'\btypescript\b', 'TypeScript'),
        (r'\bc\+\+\b', 'C++'),
        (r'\bc#\b', 'C#'),
        (r'\bruby\b', 'Ruby'),
        (r'\bgolang\b', 'Go'),  # Only match golang, not just "go"
        (r'\brust\b', 'Rust'),
        (r'\bswift\b', 'Swift'),
        (r'\bkotlin\b', 'Kotlin'),
        (r'\bphp\b', 'PHP'),
        (r'\bsolidity\b', 'Solidity'),
    ]
    for pattern, name in prog_langs:
        if re.search(pattern, resume_lower):
            skills["programming"].append(name)
    
    # AI/ML skills
    ai_skills = ['machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow', 'pytorch', 'scikit-learn', 
                 'ocr', 'llm', 'llm agents', 'agentic ai', 'predictive modeling', 'data processing', 'neural network']
    for skill in ai_skills:
        if skill in resume_text.lower():
            skills["ai_ml"].append(skill.title())
    
    # Frameworks
    frameworks = ['flask', 'django', 'fastapi', 'react', 'angular', 'vue', 'node.js', 'express', 'spring', 'opencv', 'crewai']
    for fw in frameworks:
        if fw in resume_text.lower():
            skills["frameworks"].append(fw.title() if fw != 'opencv' else 'OpenCV')
    
    # Tools
    tools = ['git', 'docker', 'kubernetes', 'aws', 'azure', 'selenium', 'beautifulsoup', 'rest api', 'jenkins', 'jira']
    for tool in tools:
        if tool in resume_text.lower():
            skills["tools"].append(tool.title())
    
    # Databases
    databases = ['mysql', 'postgresql', 'mongodb', 'sqlite', 'redis', 'elasticsearch', 'firebase']
    for db in databases:
        if db in resume_text.lower():
            skills["databases"].append(db.title() if db != 'mysql' else 'MySQL')
    
    return skills


def extract_education(resume_text: str) -> List[Dict[str, str]]:
    """Extract education details."""
    education = []
    
    # Common patterns
    degree_patterns = [
        r"(Bachelor|Master|B\.?E\.?|B\.?Tech|M\.?Tech|B\.?Sc|M\.?Sc|MBA|PhD|Diploma)[^|]*?\|?\s*(\d{4})\s*[–-]\s*(\d{4}|\d{2}|Present)",
        r"(Bachelor|Master|Diploma)[^–\n]+",
    ]
    
    lines = resume_text.split('\n')
    for i, line in enumerate(lines):
        if any(deg in line.lower() for deg in ['bachelor', 'master', 'diploma', 'b.e', 'b.tech', 'm.tech']):
            edu_entry = {
                'degree': line.strip(),
                'institution': '',
                'cgpa': ''
            }
            
            # Look for institution in next line
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if 'college' in next_line.lower() or 'university' in next_line.lower() or 'institute' in next_line.lower():
                    edu_entry['institution'] = next_line.split('|')[0].strip()
            
            # Look for CGPA
            cgpa_match = re.search(r'CGPA:\s*([\d.]+)', resume_text[resume_text.find(line):resume_text.find(line)+200], re.IGNORECASE)
            if cgpa_match:
                edu_entry['cgpa'] = cgpa_match.group(1)
            
            education.append(edu_entry)
    
    return education[:3]


def extract_achievements(resume_text: str) -> List[str]:
    """Extract achievements and awards."""
    achievements = []
    
    # Look for achievement section
    lines = resume_text.split('\n')
    in_achievements = False
    
    for line in lines:
        line = line.strip()
        
        if 'achievement' in line.lower() and len(line) < 30:
            in_achievements = True
            continue
        
        if in_achievements:
            if any(section in line.lower() for section in ['training', 'education', 'skills', 'project']):
                in_achievements = False
            elif line and len(line) > 10:
                achievements.append(line.lstrip('•-▪ '))
    
    # Also look for specific achievement keywords
    achievement_keywords = ['finalist', 'winner', 'award', 'recognition', 'certified', 'top', 'first', 'rank']
    for line in lines:
        if any(kw in line.lower() for kw in achievement_keywords):
            clean_line = line.strip().lstrip('•-▪ ')
            if clean_line and clean_line not in achievements:
                achievements.append(clean_line)
    
    return achievements[:5]


def extract_training(resume_text: str) -> List[str]:
    """Extract training and certifications."""
    training = []
    
    lines = resume_text.split('\n')
    in_training = False
    
    for line in lines:
        line = line.strip()
        
        if 'training' in line.lower() or 'certification' in line.lower():
            if len(line) < 30:
                in_training = True
                continue
        
        if in_training:
            if any(section in line.lower() for section in ['achievement', 'education', 'skills', 'project', 'experience']):
                in_training = False
            elif line and len(line) > 10:
                training.append(line.lstrip('•-▪ '))
    
    return training[:5]


def format_resume_summary(data: Dict[str, Any]) -> str:
    """Format extracted data into a readable summary for LLM."""
    
    summary = f"""
CANDIDATE: {data.get('name', 'Candidate')}

PROJECTS:
"""
    
    for i, proj in enumerate(data.get('projects', []), 1):
        summary += f"""
Project {i}: {proj.get('name', 'Project')}
- Description: {proj.get('description', '')}
- Technologies: {proj.get('tech', '')}
"""
        for detail in proj.get('details', [])[:3]:
            summary += f"- {detail}\n"
    
    summary += "\nWORK EXPERIENCE:\n"
    for exp in data.get('experience', []):
        summary += f"""
Role: {exp.get('role', '')}
Company: {exp.get('company', '')}
Duration: {exp.get('duration', '')}
Achievements:
"""
        for ach in exp.get('achievements', [])[:3]:
            summary += f"- {ach}\n"
    
    summary += "\nTECHNICAL SKILLS:\n"
    skills = data.get('skills', {})
    if skills.get('programming'):
        summary += f"Programming: {', '.join(skills['programming'])}\n"
    if skills.get('ai_ml'):
        summary += f"AI/ML: {', '.join(skills['ai_ml'])}\n"
    if skills.get('frameworks'):
        summary += f"Frameworks: {', '.join(skills['frameworks'])}\n"
    if skills.get('tools'):
        summary += f"Tools: {', '.join(skills['tools'])}\n"
    if skills.get('databases'):
        summary += f"Databases: {', '.join(skills['databases'])}\n"
    
    summary += "\nEDUCATION:\n"
    for edu in data.get('education', []):
        summary += f"- {edu.get('degree', '')} | {edu.get('institution', '')} | CGPA: {edu.get('cgpa', '')}\n"
    
    summary += "\nACHIEVEMENTS:\n"
    for ach in data.get('achievements', []):
        summary += f"- {ach}\n"
    
    summary += "\nTRAINING:\n"
    for train in data.get('training', []):
        summary += f"- {train}\n"
    
    return summary
