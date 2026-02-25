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


# Allowed MIME types → extension map
ALLOWED_TYPES = {
    "application/pdf":  ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


# ── Initialize Cloudinary (once at import) ───────────────────────────────────

def _init_cloudinary():
    cloudinary.config(
        cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
        api_key=os.environ.get("CLOUDINARY_API_KEY"),
        api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
        secure=True,  # Always use HTTPS URLs
    )
    print("[Cloudinary] Configured ✓")


_init_cloudinary()


# ── Upload Function ──────────────────────────────────────────────────────────

async def upload_resume(file) -> str:
    """
    Validate and upload a resume file to Cloudinary.

    Args:
        file: FastAPI UploadFile object

    Returns:
        Secure Cloudinary URL (str)

    Raises:
        HTTPException 400 — invalid type or file too large
        HTTPException 500 — Cloudinary upload failed
    """
    # 1. Validate content type
    content_type = file.content_type or ""
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{content_type}'. Allowed: PDF, DOCX.",
        )

    # 2. Read file as bytes
    file_bytes = await file.read()

    # 3. Validate file size (must happen AFTER reading)
    if len(file_bytes) > MAX_FILE_SIZE:
        size_mb = len(file_bytes) / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large ({size_mb:.1f} MB). Maximum allowed is 5 MB.",
        )

    # 4. Derive a clean public_id from the original filename
    original_name = (file.filename or "resume").rsplit(".", 1)[0]
    # Sanitize: keep alphanum, dashes, underscores
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in original_name)
    public_id = f"career-copilot/resumes/{safe_name}"

    # 5. Upload bytes to Cloudinary
    # IMPORTANT: resource_type="raw" is required for PDFs and DOCX files.
    # Without it, Cloudinary treats them as images and the upload fails.
    try:
        result = cloudinary.uploader.upload(
            io.BytesIO(file_bytes),
            public_id=public_id,
            resource_type="raw",      # Required for PDF/DOCX
            overwrite=True,
            use_filename=False,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cloudinary upload failed: {str(e)}",
        )

    return result["secure_url"]
