"""
Resume Parser Module
Extracts text from PDF resumes using pdfplumber
"""

import os
import tempfile
import pdfplumber
from fastapi import UploadFile


async def parse_resume(pdf_file: UploadFile) -> str:
    """
    Parse a PDF resume and extract text content.
    
    Args:
        pdf_file: FastAPI UploadFile object containing the PDF
        
    Returns:
        Extracted text from the PDF as a string
    """
    # Create a temporary file to store the uploaded PDF
    temp_path = None
    try:
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_path = temp_file.name
            content = await pdf_file.read()
            temp_file.write(content)
        
        # Extract text using pdfplumber
        extracted_text = []
        with pdfplumber.open(temp_path) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text.append(page_text)
        
        full_text = "\n\n".join(extracted_text)
        return full_text, page_count
    
    finally:
        # Clean up: delete temporary file
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


import re

def get_resume_preview(resume_text: str, page_count: int = 1) -> dict:
    """
    Extract quick stats from the parsed resume for a verification preview.
    Helps users confirm the PDF was parsed correctly.
    """
    lines = resume_text.strip().split("\n")
    words = resume_text.split()
    
    # Try to detect name (usually first non-empty line)
    detected_name = ""
    for line in lines[:5]:
        line = line.strip()
        # Skip lines that look like headers/titles, emails, phones, URLs
        if not line or "@" in line or "http" in line.lower():
            continue
        if re.match(r'^[\d\(\+]', line):  # starts with number (phone)
            continue
        if len(line.split()) <= 4 and len(line) < 50:
            # Likely a name (short, at the top)
            detected_name = line
            break
    
    # Detect email
    email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', resume_text)
    detected_email = email_match.group(0) if email_match else None
    
    # Detect phone  
    phone_match = re.search(r'[\+]?[\d\s\-\(\)]{10,15}', resume_text)
    detected_phone = phone_match.group(0).strip() if phone_match else None
    
    # Detect key sections present
    section_keywords = {
        "Education": r'education|academic|university|degree|bachelor|master|b\.tech|m\.tech',
        "Experience": r'experience|employment|work history|professional',
        "Projects": r'projects|portfolio|personal projects|academic projects',
        "Skills": r'skills|technologies|technical skills|competencies|proficiencies',
        "Certifications": r'certification|certified|certificate',
        "Achievements": r'achievements|awards|honors|accomplishments',
    }
    
    sections_found = []
    text_lower = resume_text.lower()
    for section, pattern in section_keywords.items():
        if re.search(pattern, text_lower):
            sections_found.append(section)
    
    # Extract top skills mentioned (look for common tech terms)
    common_skills = [
        "Python", "Java", "JavaScript", "TypeScript", "React", "Angular", "Vue",
        "Node.js", "Django", "Flask", "FastAPI", "Spring", "SQL", "NoSQL", 
        "MongoDB", "PostgreSQL", "MySQL", "AWS", "Azure", "GCP", "Docker",
        "Kubernetes", "Git", "Linux", "TensorFlow", "PyTorch", "Pandas",
        "NumPy", "Scikit-learn", "HTML", "CSS", "Tailwind", "REST", "GraphQL",
        "Redis", "Kafka", "Elasticsearch", "C++", "C#", "Go", "Rust", "Swift",
        "Kotlin", "PHP", "Ruby", "Scala", "R", "MATLAB", "Tableau", "Power BI",
        "Figma", "Jira", "Jenkins", "CI/CD", "Terraform", "Ansible",
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    ]
    
    found_skills = []
    for skill in common_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', resume_text, re.IGNORECASE):
            found_skills.append(skill)
    
    return {
        "detected_name": detected_name,
        "page_count": page_count,
        "word_count": len(words),
        "email": detected_email,
        "phone": detected_phone,
        "sections_found": sections_found,
        "skills_detected": found_skills[:15],  # cap at 15
        "text_length": len(resume_text)
    }

