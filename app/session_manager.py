"""
Session Manager
Per-user session storage using cookie-based session IDs.
Uses file-based storage so sessions persist across restarts
and are shared across Gunicorn workers.
"""

import uuid
import time
import json
import threading
from pathlib import Path
from typing import Any, Dict, Optional

# File-based session store directory
SESSION_DIR = Path(__file__).parent / "data" / "sessions"
SESSION_DIR.mkdir(parents=True, exist_ok=True)

# Session configuration
SESSION_COOKIE_NAME = "career_copilot_session"
SESSION_MAX_AGE = 3600 * 4  # 4 hours

# Lock for file operations within a single process
_file_lock = threading.Lock()


def _session_file(session_id: str) -> Path:
    """Get the file path for a session ID (sanitized)."""
    # Sanitize: only allow UUID characters
    safe_id = "".join(c for c in session_id if c in "0123456789abcdef-")
    return SESSION_DIR / f"{safe_id}.json"


def _read_session(session_id: str) -> Dict[str, Any]:
    """Read session data from file. Returns empty dict if not found or expired."""
    path = _session_file(session_id)
    if not path.exists():
        return {}
    
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        
        # Check expiration
        created = data.get("_created_at", 0)
        if time.time() - created > SESSION_MAX_AGE:
            # Session expired — clean up
            try:
                path.unlink()
            except OSError:
                pass
            return {}
        
        return data
    except (json.JSONDecodeError, OSError):
        return {}


def _write_session(session_id: str, data: Dict[str, Any]):
    """Write session data to file."""
    path = _session_file(session_id)
    with _file_lock:
        path.write_text(json.dumps(data, default=str), encoding="utf-8")


def _cleanup_expired():
    """Remove expired session files to prevent disk bloat."""
    now = time.time()
    try:
        for path in SESSION_DIR.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                created = data.get("_created_at", 0)
                if now - created > SESSION_MAX_AGE:
                    path.unlink()
            except (json.JSONDecodeError, OSError):
                # Corrupt file — remove it
                try:
                    path.unlink()
                except OSError:
                    pass
    except Exception:
        pass


def get_session_id(request) -> Optional[str]:
    """Extract session ID from request cookies."""
    return request.cookies.get(SESSION_COOKIE_NAME)


def get_session(request) -> Dict[str, Any]:
    """Get session data for the current request."""
    session_id = get_session_id(request)
    
    if session_id:
        return _read_session(session_id)
    
    return {}


def create_session() -> str:
    """Create a new session and return its ID."""
    # Periodic cleanup: check file count
    try:
        file_count = len(list(SESSION_DIR.glob("*.json")))
        if file_count > 100:
            _cleanup_expired()
    except Exception:
        pass
    
    session_id = str(uuid.uuid4())
    data = {
        "_created_at": time.time(),
        "resume_text": "",
        "role": "",
        "analysis": None,
    }
    _write_session(session_id, data)
    return session_id


def set_session_data(request, key: str, value: Any):
    """Set a value in the current session."""
    session_id = get_session_id(request)
    if not session_id:
        return
    
    data = _read_session(session_id)
    if data:
        data[key] = value
        _write_session(session_id, data)


def get_session_data(request, key: str, default: Any = None) -> Any:
    """Get a value from the current session."""
    session = get_session(request)
    return session.get(key, default)


def update_session(session_id: str, updates: Dict[str, Any]):
    """Directly update a session by ID (used during initial creation)."""
    data = _read_session(session_id)
    if data:
        data.update(updates)
        _write_session(session_id, data)


def set_session_cookie(response, session_id: str):
    """Set the session cookie on a response."""
    import os
    is_production = os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("RENDER")
    
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=bool(is_production),  # Secure in production (HTTPS)
    )
    return response
