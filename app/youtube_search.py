"""
YouTube Search Module
Provides curated video recommendations for skills
"""

import urllib.parse


# Curated video database - specific videos for common skills
SKILL_VIDEOS = {
    # Frontend Skills
    "react": [
        {"title": "React Tutorial for Beginners", "id": "SqcY0GlETPk", "channel": "Programming with Mosh"},
        {"title": "React Full Course 2024", "id": "CgkZ7MvWUAA", "channel": "freeCodeCamp"},
    ],
    "javascript": [
        {"title": "JavaScript Tutorial Full Course", "id": "EfAl9bwzVZk", "channel": "Bro Code"},
        {"title": "JavaScript Crash Course", "id": "hdI2bqOjy3c", "channel": "Traversy Media"},
    ],
    "html": [
        {"title": "HTML Full Course", "id": "kUMe1FH4CHE", "channel": "freeCodeCamp"},
        {"title": "HTML Tutorial for Beginners", "id": "qz0aGYrrlhU", "channel": "Programming with Mosh"},
    ],
    "css": [
        {"title": "CSS Tutorial Full Course", "id": "n4R2E7O-Ngo", "channel": "Bro Code"},
        {"title": "CSS Crash Course", "id": "yfoY53QXEnI", "channel": "Traversy Media"},
    ],
    "typescript": [
        {"title": "TypeScript Full Course", "id": "30LWjhZzg50", "channel": "freeCodeCamp"},
        {"title": "TypeScript Tutorial", "id": "BCg4U1FzODs", "channel": "Traversy Media"},
    ],
    "vue": [
        {"title": "Vue.js Course for Beginners", "id": "FXpIoQ_rT_c", "channel": "freeCodeCamp"},
        {"title": "Vue 3 Crash Course", "id": "ZqgiuPt5QZo", "channel": "Traversy Media"},
    ],
    "responsive design": [
        {"title": "Responsive Web Design", "id": "srvUrASNj0s", "channel": "freeCodeCamp"},
    ],
    
    # Data Skills
    "python": [
        {"title": "Python Tutorial for Beginners", "id": "_uQrJ0TkZlc", "channel": "Programming with Mosh"},
        {"title": "Python Full Course", "id": "XKHEtdqhLK8", "channel": "Bro Code"},
    ],
    "sql": [
        {"title": "SQL Tutorial Full Course", "id": "HXV3zeQKqGY", "channel": "freeCodeCamp"},
        {"title": "SQL for Beginners", "id": "7S_tz1z_5bA", "channel": "Programming with Mosh"},
    ],
    "excel": [
        {"title": "Excel Tutorial for Beginners", "id": "Vl0H-qTclOg", "channel": "Kevin Stratvert"},
        {"title": "Excel Full Course", "id": "27dxBp0EgCc", "channel": "Simplilearn"},
    ],
    "tableau": [
        {"title": "Tableau Full Course", "id": "aHaOIvR00So", "channel": "Simplilearn"},
        {"title": "Tableau Tutorial for Beginners", "id": "jEgVto5QME8", "channel": "freeCodeCamp"},
    ],
    "power bi": [
        {"title": "Power BI Full Course", "id": "3u7MQz1EyPY", "channel": "Simplilearn"},
        {"title": "Power BI Tutorial", "id": "AGrl-H87pRU", "channel": "Kevin Stratvert"},
    ],
    "pandas": [
        {"title": "Pandas Tutorial", "id": "vmEHCJofslg", "channel": "Keith Galli"},
        {"title": "Pandas Full Course", "id": "PcvsOaixUh8", "channel": "freeCodeCamp"},
    ],
    "statistics": [
        {"title": "Statistics Full Course", "id": "xxpc-HPKN28", "channel": "freeCodeCamp"},
        {"title": "Statistics Fundamentals", "id": "qBigTkBLU6g", "channel": "StatQuest"},
    ],
    "data visualization": [
        {"title": "Data Visualization with Python", "id": "r-uOLxNrNk8", "channel": "freeCodeCamp"},
    ],
    
    # Backend/DevOps Skills
    "node.js": [
        {"title": "Node.js Tutorial", "id": "TlB_eWDSMt4", "channel": "Programming with Mosh"},
        {"title": "Node.js Full Course", "id": "Oe421EPjeBE", "channel": "freeCodeCamp"},
    ],
    "docker": [
        {"title": "Docker Tutorial for Beginners", "id": "pTFZFxd4hOI", "channel": "Programming with Mosh"},
        {"title": "Docker Full Course", "id": "fqMOX6JJhGo", "channel": "freeCodeCamp"},
    ],
    "aws": [
        {"title": "AWS Tutorial for Beginners", "id": "k1RI5locZE4", "channel": "freeCodeCamp"},
        {"title": "AWS Certified Cloud Practitioner", "id": "SOTamWNgDKc", "channel": "freeCodeCamp"},
    ],
    "git": [
        {"title": "Git and GitHub for Beginners", "id": "RGOj5yH7evk", "channel": "freeCodeCamp"},
        {"title": "Git Tutorial", "id": "8JJ101D3knE", "channel": "Programming with Mosh"},
    ],
    "api": [
        {"title": "APIs for Beginners", "id": "GZvSYJDk-us", "channel": "freeCodeCamp"},
        {"title": "REST API Tutorial", "id": "lsMQRaeKNDk", "channel": "freeCodeCamp"},
    ],
    "database design": [
        {"title": "Database Design Course", "id": "ztHopE5Wnpc", "channel": "freeCodeCamp"},
    ],
    
    # ML/AI Skills
    "machine learning": [
        {"title": "Machine Learning Course", "id": "NWONeJKn6kc", "channel": "freeCodeCamp"},
        {"title": "Machine Learning Tutorial", "id": "7eh4d6sabA0", "channel": "Programming with Mosh"},
    ],
    "tensorflow": [
        {"title": "TensorFlow 2.0 Complete Course", "id": "tPYj3fFJGjk", "channel": "freeCodeCamp"},
    ],
    "pytorch": [
        {"title": "PyTorch Full Course", "id": "V_xro1bcAuA", "channel": "freeCodeCamp"},
    ],
    
    # Soft Skills
    "agile": [
        {"title": "Agile Project Management", "id": "Z9QbYZh1YXY", "channel": "Google Career Certificates"},
    ],
    "communication": [
        {"title": "Communication Skills", "id": "HAnw168huqA", "channel": "TED"},
    ],
    "leadership": [
        {"title": "Leadership Skills", "id": "18UVXW-x2_8", "channel": "Simon Sinek"},
    ],
}


def get_youtube_video_url(video_id: str) -> str:
    """Generate a YouTube watch URL from video ID."""
    return f"https://www.youtube.com/watch?v={video_id}"


def get_youtube_search_url(query: str) -> str:
    """Generate a YouTube search URL for a query."""
    encoded_query = urllib.parse.quote(query)
    return f"https://www.youtube.com/results?search_query={encoded_query}"


def find_matching_videos(skill_name: str) -> list:
    """Find curated videos that match the skill name."""
    skill_lower = skill_name.lower()
    
    # Direct match
    if skill_lower in SKILL_VIDEOS:
        return SKILL_VIDEOS[skill_lower]
    
    # Partial match - check if skill contains any known skill
    for known_skill, videos in SKILL_VIDEOS.items():
        if known_skill in skill_lower or skill_lower in known_skill:
            return videos
    
    return []


def get_video_recommendations(skills: list, target_role: str) -> list:
    """
    Generate video recommendations for each skill.
    Returns curated videos when available, search links as fallback.
    """
    recommendations = []
    
    for skill in skills:
        if isinstance(skill, dict):
            skill_name = skill.get("skill", "")
        else:
            skill_name = skill
        
        if not skill_name:
            continue
        
        # Find curated videos
        curated_videos = find_matching_videos(skill_name)
        
        if curated_videos:
            # Use curated specific videos
            videos = []
            for video in curated_videos[:2]:  # Max 2 videos per skill
                videos.append({
                    "title": video["title"],
                    "url": get_youtube_video_url(video["id"]),
                    "channel": video["channel"],
                    "is_curated": True
                })
            
            recommendation = {
                "skill": skill_name,
                "videos": videos,
                "search_url": get_youtube_search_url(f"{skill_name} tutorial")
            }
        else:
            # Fallback to search URLs
            recommendation = {
                "skill": skill_name,
                "videos": [
                    {
                        "title": f"Search: {skill_name} tutorial",
                        "url": get_youtube_search_url(f"{skill_name} tutorial for beginners"),
                        "channel": "YouTube Search",
                        "is_curated": False
                    }
                ],
                "search_url": get_youtube_search_url(f"{skill_name} tutorial")
            }
        
        recommendations.append(recommendation)
    
    return recommendations


def get_curated_channels(target_role: str) -> list:
    """Return curated YouTube channels based on target role."""
    channels = {
        "Frontend Developer": [
            {"name": "Traversy Media", "url": "https://www.youtube.com/@TraversyMedia"},
            {"name": "Web Dev Simplified", "url": "https://www.youtube.com/@WebDevSimplified"},
            {"name": "Fireship", "url": "https://www.youtube.com/@Fireship"}
        ],
        "Data Analyst": [
            {"name": "Alex The Analyst", "url": "https://www.youtube.com/@AlexTheAnalyst"},
            {"name": "StatQuest", "url": "https://www.youtube.com/@statquest"},
            {"name": "freeCodeCamp", "url": "https://www.youtube.com/@freecodecamp"}
        ],
        "Backend Developer": [
            {"name": "Traversy Media", "url": "https://www.youtube.com/@TraversyMedia"},
            {"name": "TechWorld with Nana", "url": "https://www.youtube.com/@TechWorldwithNana"},
            {"name": "Fireship", "url": "https://www.youtube.com/@Fireship"}
        ],
        "Full Stack Developer": [
            {"name": "Traversy Media", "url": "https://www.youtube.com/@TraversyMedia"},
            {"name": "The Net Ninja", "url": "https://www.youtube.com/@NetNinja"},
            {"name": "Fireship", "url": "https://www.youtube.com/@Fireship"}
        ],
        "Machine Learning Engineer": [
            {"name": "3Blue1Brown", "url": "https://www.youtube.com/@3blue1brown"},
            {"name": "Sentdex", "url": "https://www.youtube.com/@sentdex"},
            {"name": "StatQuest", "url": "https://www.youtube.com/@statquest"}
        ],
        "DevOps Engineer": [
            {"name": "TechWorld with Nana", "url": "https://www.youtube.com/@TechWorldwithNana"},
            {"name": "NetworkChuck", "url": "https://www.youtube.com/@NetworkChuck"},
            {"name": "KodeKloud", "url": "https://www.youtube.com/@KodeKloud"}
        ],
        "Product Manager": [
            {"name": "Product School", "url": "https://www.youtube.com/@ProductSchoolSanFrancisco"},
            {"name": "Lenny's Podcast", "url": "https://www.youtube.com/@LennysPodcast"},
            {"name": "The Futur", "url": "https://www.youtube.com/@thefutur"}
        ],
        "UX Designer": [
            {"name": "The Futur", "url": "https://www.youtube.com/@thefutur"},
            {"name": "DesignCourse", "url": "https://www.youtube.com/@DesignCourse"},
            {"name": "Flux Academy", "url": "https://www.youtube.com/@FluxAcademy"}
        ]
    }
    
    return channels.get(target_role, channels["Frontend Developer"])
