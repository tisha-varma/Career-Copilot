"""
cloudinary_storage.py
---------------------
Cloudinary file upload helper for Career Copilot.

Flow:
  FastAPI receives file → read as bytes → validate → upload to Cloudinary → return URL

IMPORTANT:
  - Upload file.read() bytes, NOT the FastAPI UploadFile object
  - Always set resource_type="raw" for PDFs and DOCX files
  - Check file size BEFORE uploading to avoid timeout on large files
"""

import os
import io
import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, status
from pathlib import Path
from dotenv import load_dotenv


# ── Initialize Environment ──────────────────────────────────────────────────
# Ensure .env is loaded even if this module is imported before main.py finishes
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()


# Allowed MIME types → extension map
ALLOWED_TYPES = {
    "application/pdf":  ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


# ── Initialize Cloudinary (once at import) ───────────────────────────────────

def _init_cloudinary():
    # Strip whitespace from keys to prevent Railway paste errors
    cloud_name = (os.environ.get("CLOUDINARY_CLOUD_NAME") or "").strip()
    api_key = (os.environ.get("CLOUDINARY_API_KEY") or "").strip()
    api_secret = (os.environ.get("CLOUDINARY_API_SECRET") or "").strip()

    if not all([cloud_name, api_key, api_secret]):
        print("[Cloudinary] Warning: Missing Cloudinary environment variables. Uploads will be disabled.")
        return

    try:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )
        print("[Cloudinary] Configured ✓")
    except Exception as e:
        print(f"[Cloudinary] Error: Failed to configure Cloudinary: {e}")


_init_cloudinary()


# ── Upload Function ──────────────────────────────────────────────────────────

async def upload_resume(file=None, *, file_bytes: bytes = None, filename: str = None, content_type: str = None) -> str:
    """
    Validate and upload a resume file to Cloudinary.

    Args:
        file:         FastAPI UploadFile object (legacy — avoid for reliability)
        file_bytes:   Pre-read raw PDF bytes (preferred — avoids stream corruption)
        filename:     Original filename (required when using file_bytes)
        content_type: MIME type (required when using file_bytes)

    Returns:
        Secure Cloudinary URL (str)

    Raises:
        HTTPException 400 — invalid type or file too large
        HTTPException 500 — Cloudinary upload failed
    """
    # Resolve parameters — prefer explicit bytes over re-reading UploadFile
    if file_bytes is None:
        if file is None:
            raise HTTPException(status_code=400, detail="No file provided.")
        content_type = content_type or file.content_type or ""
        filename = filename or file.filename or "resume"
        await file.seek(0)
        file_bytes = await file.read()
    else:
        content_type = content_type or "application/pdf"
        filename = filename or "resume.pdf"

    # 1. Validate content type
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{content_type}'. Allowed: PDF, DOCX.",
        )

    # 2. Validate file size
    if len(file_bytes) > MAX_FILE_SIZE:
        size_mb = len(file_bytes) / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large ({size_mb:.1f} MB). Maximum allowed is 5 MB.",
        )

    # 3. Derive a clean public_id
    original_name = filename.rsplit(".", 1)[0]
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in original_name)
    
    print(f"[Cloudinary] Uploading {len(file_bytes)} bytes for '{filename}' as {safe_name}")

    # 4. Upload bytes to Cloudinary
    try:
        result = cloudinary.uploader.upload(
            io.BytesIO(file_bytes),
            public_id=safe_name,
            folder="career-copilot/resumes",
            resource_type="raw",      # Serve PDFs as raw files so browsers can display them natively
            overwrite=True,
            use_filename=True,
            unique_filename=True      # Use unique IDs to avoid browser cache issues
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cloudinary upload failed: {str(e)}",
        )

    return result["secure_url"]
