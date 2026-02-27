"""
firestore_db.py
---------------
Firestore helper functions for Career Copilot.

Collections:
  - users       : user profile documents
  - files       : uploaded resume metadata
  - audit_logs  : user action history

All functions are synchronous wrappers — Railway has no async Firestore client.
"""

from datetime import datetime, timezone
from google.cloud.exceptions import NotFound
from firebase_admin import firestore


# ── Firestore Client ─────────────────────────────────────────────────────────

def _get_db():
    """Return (or lazily create) the Firestore client."""
    return firestore.client()


# ── Users Collection ─────────────────────────────────────────────────────────

def create_or_update_user(uid: str, name: str, email: str, picture: str) -> dict:
    """
    Create the user document if it doesn't exist, or update name/email/picture.

    Fields:
        uid, name, email, profile_picture, created_at (only set on first write)

    Returns:
        The user document as a dict.
    """
    db = _get_db()
    ref = db.collection("users").document(uid)
    doc = ref.get()

    if doc.exists:
        # Update mutable fields only
        ref.update({
            "name":            name,
            "email":           email,
            "profile_picture": picture,
        })
    else:
        # First login — create full document
        ref.set({
            "uid":             uid,
            "name":            name,
            "email":           email,
            "profile_picture": picture,
            "created_at":      datetime.now(timezone.utc).isoformat(),
        })

    return ref.get().to_dict()


def delete_user(uid: str) -> bool:
    """Delete a user document."""
    db = _get_db()
    db.collection("users").document(uid).delete()
    return True


def get_user(uid: str) -> dict | None:
    """
    Fetch a user document by uid.

    Returns:
        User dict or None if not found.
    """
    db = _get_db()
    doc = db.collection("users").document(uid).get()
    return doc.to_dict() if doc.exists else None


# ── Files Collection ─────────────────────────────────────────────────────────

def save_file_metadata(uid: str, file_name: str, file_url: str) -> dict:
    """
    Save uploaded resume metadata to the files collection.

    Fields:
        id, uid, file_name, file_url, uploaded_at

    Returns:
        The saved document as a dict (including auto-generated id).
    """
    db = _get_db()
    ref = db.collection("files").document()  # auto-generated ID

    data = {
        "id":          ref.id,
        "uid":         uid,
        "file_name":   file_name,
        "file_url":    file_url,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
    ref.set(data)
    return data


def get_user_files(uid: str) -> list[dict]:
    """
    Return all file records for a given user, sorted newest-first.

    Returns:
        List of file dicts.
    """
    db = _get_db()
    docs = (
        db.collection("files")
        .where("uid", "==", uid)
        .order_by("uploaded_at", direction=firestore.Query.DESCENDING)
        .stream()
    )
    return [doc.to_dict() for doc in docs]


def get_all_users() -> list[dict]:
    """
    Return all user profiles in the system.
    Sorts by created_at in Python to ensure documents without the field are still returned.
    """
    db = _get_db()
    docs = db.collection("users").stream()
    users = [doc.to_dict() for doc in docs]
    # Sort by created_at desc, handle missing keys gracefully
    users.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return users


def get_all_files() -> list[dict]:
    """
    Return all uploaded file records across all users.
    Sorts by uploaded_at in Python to be resilient to missing fields.
    """
    db = _get_db()
    docs = db.collection("files").stream()
    files = [doc.to_dict() for doc in docs]
    files.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)
    return files


def delete_file(file_id: str) -> bool:
    """Delete a file metadata document."""
    db = _get_db()
    db.collection("files").document(file_id).delete()
    return True


# ── Audit Logs Collection ────────────────────────────────────────────────────

def save_audit_log(uid: str, action: str, details: str) -> None:
    """
    Persist a single audit log entry.

    Called internally by audit.py — do not call directly.
    """
    db = _get_db()
    ref = db.collection("audit_logs").document()

    ref.set({
        "id":        ref.id,
        "uid":       uid,
        "action":    action,       # e.g. "LOGIN", "UPLOAD_RESUME"
        "details":   details,      # e.g. filename or description
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


def get_audit_logs(uid: str) -> list[dict]:
    """
    Return all audit log entries for a user, sorted newest-first.

    Returns:
        List of audit log dicts.
    """
    db = _get_db()
    docs = (
        db.collection("audit_logs")
        .where("uid", "==", uid)
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .stream()
    )
    return [doc.to_dict() for doc in docs]


def get_all_audit_logs() -> list[dict]:
    """
    Return all audit log entries across the entire system.
    """
    db = _get_db()
    docs = db.collection("audit_logs").stream()
    logs = [doc.to_dict() for doc in docs]
    # Sort by timestamp desc, fallback to empty string
    logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return logs


def delete_audit_log(log_id: str) -> bool:
    """Delete a single audit log entry."""
    db = _get_db()
    db.collection("audit_logs").document(log_id).delete()
    return True
