"""
firebase_auth.py
----------------
Firebase Admin SDK initialization and token verification.

Provides:
  - verify_firebase_token(token) → decoded user dict
  - get_current_user(request)    → FastAPI Depends() for protected routes
"""

import os
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Request, HTTPException, status


# ── Initialize Firebase Admin SDK (once) ────────────────────────────────────

def _init_firebase():
    """
    Build Firebase credentials from environment variables.
    """
    if firebase_admin._apps:
        return

    # Check if we have the minimum required vars to even try
    project_id = os.environ.get("FIREBASE_PROJECT_ID")
    client_email = os.environ.get("FIREBASE_CLIENT_EMAIL")
    private_key = os.environ.get("FIREBASE_PRIVATE_KEY")

    if not all([project_id, client_email, private_key]):
        print("[Firebase] Warning: Missing FIREBASE_PROJECT_ID, CLIENT_EMAIL, or PRIVATE_KEY. Auth features will be disabled.")
        return

    try:
        # Fix Railway / .env private key line-break encoding
        fixed_private_key = private_key.replace("\\n", "\n")

        cert_dict = {
            "type": "service_account",
            "project_id": project_id,
            "private_key": fixed_private_key,
            "client_email": client_email,
            "token_uri": "https://oauth2.googleapis.com/token",
        }

        cert = credentials.Certificate(cert_dict)
        firebase_admin.initialize_app(cert)
        print("[Firebase] Admin SDK initialized ✓")
    except Exception as e:
        print(f"[Firebase] Error: Failed to initialize Admin SDK: {e}")


# Run initialization at import time
_init_firebase()


# ── Token Verification ───────────────────────────────────────────────────────

def verify_firebase_token(token: str) -> dict:
    """
    Verify a Firebase ID token and return the decoded user payload.

    Args:
        token: Raw Firebase ID token string (without 'Bearer ' prefix)

    Returns:
        dict with keys: uid, name, email, picture

    Raises:
        HTTPException 401 if token is invalid or expired
    """
    try:
        decoded = auth.verify_id_token(token)
        return {
            "uid":     decoded.get("uid"),
            "name":    decoded.get("name", ""),
            "email":   decoded.get("email", ""),
            "picture": decoded.get("picture", ""),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired Firebase token: {str(e)}",
        )


# ── FastAPI Dependency ───────────────────────────────────────────────────────

async def get_current_user(request: Request) -> dict:
    """
    FastAPI dependency — extracts and verifies the Firebase ID token
    from the Authorization header.

    Frontend must send:
        Authorization: Bearer <FIREBASE_ID_TOKEN>

    Usage in a route:
        @app.get("/profile")
        async def profile(user=Depends(get_current_user)):
            ...

    Raises:
        HTTPException 401 if header is missing or token is invalid
    """
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header. Expected: 'Bearer <token>'",
        )

    # Extract token — everything after "Bearer "
    token = auth_header.split(" ", 1)[1].strip()

    return verify_firebase_token(token)
