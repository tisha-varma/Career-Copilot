"""
Resume Storage
Saves uploaded resumes locally with metadata for record-keeping.
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional


# Storage directory
STORAGE_DIR = Path(__file__).parent / "data" / "resumes"
METADATA_FILE = STORAGE_DIR / "_metadata.json"


def _ensure_storage():
    """Create storage directory if it doesn't exist."""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    if not METADATA_FILE.exists():
        METADATA_FILE.write_text("[]", encoding="utf-8")


def save_resume(
    file_bytes: bytes,
    original_filename: str,
    target_role: str,
    detected_name: Optional[str] = None,
    detected_email: Optional[str] = None,
) -> str:
    """
    Save an uploaded resume file and record metadata.
    
    Args:
        file_bytes: Raw file content
        original_filename: Original upload filename
        target_role: The role the user selected
        detected_name: Name extracted from resume (if any)
        detected_email: Email extracted from resume (if any)
    
    Returns:
        The saved filename
    """
    _ensure_storage()
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_hash = hashlib.md5(file_bytes).hexdigest()[:8]
    ext = Path(original_filename).suffix.lower() or ".pdf"
    
    # Clean the detected name for filename
    name_part = ""
    if detected_name:
        name_part = "_" + "".join(c if c.isalnum() else "_" for c in detected_name)[:30]
    
    saved_name = f"{timestamp}{name_part}_{file_hash}{ext}"
    save_path = STORAGE_DIR / saved_name
    
    # Save the file
    save_path.write_bytes(file_bytes)
    
    # Record metadata
    entry = {
        "filename": saved_name,
        "original_name": original_filename,
        "target_role": target_role,
        "detected_name": detected_name or "Unknown",
        "detected_email": detected_email or "",
        "file_size_kb": round(len(file_bytes) / 1024, 1),
        "uploaded_at": datetime.now().isoformat(),
    }
    
    try:
        metadata = json.loads(METADATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        metadata = []
    
    metadata.append(entry)
    METADATA_FILE.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    
    print(f"[ResumeStorage] Saved: {saved_name} ({entry['file_size_kb']}KB) "
          f"— {entry['detected_name']} → {target_role}")
    
    return saved_name


def get_resume_count() -> int:
    """Get total number of stored resumes."""
    _ensure_storage()
    try:
        metadata = json.loads(METADATA_FILE.read_text(encoding="utf-8"))
        return len(metadata)
    except Exception:
        return 0


def get_recent_uploads(limit: int = 20) -> list:
    """Get recent upload metadata."""
    _ensure_storage()
    try:
        metadata = json.loads(METADATA_FILE.read_text(encoding="utf-8"))
        return metadata[-limit:]
    except Exception:
        return []
