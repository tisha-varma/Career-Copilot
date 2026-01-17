"""
Job Search Module
Generate job search URLs for various platforms
"""

import urllib.parse


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
