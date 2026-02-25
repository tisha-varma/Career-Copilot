"""
audit.py
--------
Reusable audit logging for Career Copilot.

Usage:
    from audit import log_action

    log_action(uid="user123", action="LOGIN", details="Google login")
    log_action(uid="user123", action="UPLOAD_RESUME", details="resume.pdf")
    log_action(uid="user123", action="UPDATE_PROFILE", details="Updated name")

Tracked actions:
    LOGIN
    UPLOAD_RESUME
    UPDATE_PROFILE
"""

from firestore_db import save_audit_log


def log_action(uid: str, action: str, details: str = "") -> None:
    """
    Write an audit log entry to Firestore.

    Args:
        uid     : Firebase UID of the user
        action  : Action name (e.g. "LOGIN", "UPLOAD_RESUME")
        details : Human-readable description or filename

    Errors are suppressed so audit failures never break main request flow.
    """
    try:
        save_audit_log(uid=uid, action=action, details=details)
    except Exception as e:
        # Log to console but don't raise — auditing must never break the app
        print(f"[Audit] Warning: could not log action '{action}' for uid '{uid}': {e}")
