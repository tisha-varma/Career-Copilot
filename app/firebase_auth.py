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
from pathlib import Path
from dotenv import load_dotenv

# ── Initialize Firebase Admin SDK (once) ────────────────────────────────────

# Ensure .env is loaded even if this module is imported before main.py finishes
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# Track initialization status for better debugging
_init_error = None

def _init_firebase():
    """
    Build Firebase credentials from environment variables safely.
    """
    global _init_error
    
    # Correct way to check if 'default' app exists
    try:
        firebase_admin.get_app()
        return # Already exists
    except ValueError:
        pass # Doesn't exist, proceed

    # Check for variables
    project_id = os.environ.get("FIREBASE_PROJECT_ID")
    client_email = os.environ.get("FIREBASE_CLIENT_EMAIL")
    private_key = os.environ.get("FIREBASE_PRIVATE_KEY")

    if not all([project_id, client_email, private_key]):
        missing = [k for k, v in {
            "FIREBASE_PROJECT_ID": project_id,
            "FIREBASE_CLIENT_EMAIL": client_email,
            "FIREBASE_PRIVATE_KEY": private_key
        }.items() if not v]
        _init_error = f"Missing environment variables: {', '.join(missing)}"
        print(f"[Firebase] Warning: {_init_error}")
        return

    try:
        # Fix line-break encoding for private key
        fixed_private_key = private_key.replace("\\n", "\n")
        # Strip potential wrapping quotes
        if fixed_private_key.startswith('"') and fixed_private_key.endswith('"'):
            fixed_private_key = fixed_private_key[1:-1]

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
        _init_error = f"Failed to initialize Admin SDK: {str(e)}"
        print(f"[Firebase] Error: {_init_error}")


# Run initialization
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
    if _init_error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Firebase not initialized: {_init_error}",
        )

    try:
        decoded = auth.verify_id_token(token)
        return {
            "uid":     decoded.get("uid"),
            "name":    decoded.get("name", ""),
            "email":   decoded.get("email", ""),
            "picture": decoded.get("picture", ""),
        }
    except Exception as e:
        # If we got here but initialize_app succeeded, it's likely a token issue
        # However, checking if apps still exist just in case
        if not firebase_admin._apps:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Firebase app was not initialized correctly. Check credentials.",
            )
            
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
