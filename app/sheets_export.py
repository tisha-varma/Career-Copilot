"""
Google Sheets Export Module
Generate data for direct paste into Google Sheets
"""

from datetime import datetime


def generate_tsv_content(analysis: dict) -> str:
    """
    Generate TSV (tab-separated) content that can be pasted directly into Google Sheets.
    """
    lines = []
    
    # Header
    target_role = analysis.get("target_role", "Unknown Role")
    score = analysis.get("role_fit_score", 0)
    
    lines.append(f"Career Analysis Report\t\t")
    lines.append(f"Generated\t{datetime.now().strftime('%Y-%m-%d %H:%M')}\t")
    lines.append(f"Target Role\t{target_role}\t")
    lines.append(f"Role Fit Score\t{score}%\t")
    lines.append("\t\t")
    
    # Strengths
    lines.append("STRENGTHS\t\t")
    for strength in analysis.get("strengths", []):
        lines.append(f"✓\t{strength}\t")
    lines.append("\t\t")
    
    # Skill Gaps
    lines.append("SKILLS TO DEVELOP\t\t")
    for skill in analysis.get("skill_gaps", {}).get("core", []):
        lines.append(f"Core\t{skill}\t")
    for skill in analysis.get("skill_gaps", {}).get("supporting", []):
        lines.append(f"Supporting\t{skill}\t")
    lines.append("\t\t")
    
    # Roadmap
    lines.append("LEARNING ROADMAP\t\t")
    lines.append("Skill\tPriority\tEstimated Time")
    for item in analysis.get("roadmap", []):
        skill = item.get("skill", "")
        priority = item.get("priority", "")
        time = item.get("estimated_time", "")
        lines.append(f"{skill}\t{priority}\t{time}")
    lines.append("\t\t")
    
    # AI Insight
    lines.append("AI MENTOR INSIGHT\t\t")
    reflection = analysis.get("reflection", {})
    reason = reflection.get("reason", "").replace("\n", " ")
    lines.append(f"\t{reason}\t")
    
    return "\n".join(lines)


def generate_sheets_data(analysis: dict) -> dict:
    """
    Generate data structure for Google Sheets export via JavaScript.
    """
    return {
        "tsv": generate_tsv_content(analysis),
        "sheets_url": "https://docs.google.com/spreadsheets/create"
    }
