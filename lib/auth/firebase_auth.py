"""
Firebase authentication operations. Pure Python — NO streamlit imports.

Uses Firebase REST API for client-side sign-in/sign-up (Admin SDK
cannot do email/password auth). Uses Admin SDK for Firestore reads
(user approval status).
"""

import logging
from datetime import datetime, timezone

import requests

from lib.auth.firebase_init import get_firestore_client

logger = logging.getLogger(__name__)

_AUTH_BASE = "https://identitytoolkit.googleapis.com/v1/accounts"
_TOKEN_BASE = "https://securetoken.googleapis.com/v1/token"
_TIMEOUT = 10


def refresh_id_token(refresh_token: str, api_key: str) -> dict:
    """Exchange a refresh token for a fresh ID token.

    Returns:
        {"id_token": str, "refresh_token": str, "uid": str}

    Raises:
        AuthError on failure.
    """
    url = f"{_TOKEN_BASE}?key={api_key}"
    body = {"grant_type": "refresh_token", "refresh_token": refresh_token}
    resp = requests.post(url, data=body, timeout=_TIMEOUT)
    data = resp.json()
    if "error" in data:
        msg = _friendly_error(data["error"].get("message", "Unknown error"))
        raise AuthError(msg, data["error"].get("message", ""))
    return {
        "id_token": data.get("id_token", ""),
        "refresh_token": data.get("refresh_token", refresh_token),
        "uid": data.get("user_id", ""),
    }


class AuthError(Exception):
    """Authentication error with user-friendly message."""

    def __init__(self, message: str, code: str = ""):
        self.message = message
        self.code = code
        super().__init__(message)


# ── Client-side auth (REST API) ──────────────────────────────


def sign_up(email: str, password: str, api_key: str) -> dict:
    """Create a new user via Firebase Auth REST API.

    Returns:
        {"uid": str, "email": str, "id_token": str, "refresh_token": str}

    Raises:
        AuthError on failure.
    """
    url = f"{_AUTH_BASE}:signUp?key={api_key}"
    body = {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    }
    resp = requests.post(url, json=body, timeout=_TIMEOUT)
    data = resp.json()

    if "error" in data:
        msg = _friendly_error(data["error"].get("message", "Unknown error"))
        raise AuthError(msg, data["error"].get("message", ""))

    return {
        "uid": data["localId"],
        "email": data["email"],
        "id_token": data["idToken"],
        "refresh_token": data["refreshToken"],
    }


def sign_in(email: str, password: str, api_key: str) -> dict:
    """Authenticate via Firebase Auth REST API.

    Returns:
        {"uid": str, "email": str, "id_token": str, "refresh_token": str}

    Raises:
        AuthError on failure.
    """
    url = f"{_AUTH_BASE}:signInWithPassword?key={api_key}"
    body = {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    }
    resp = requests.post(url, json=body, timeout=_TIMEOUT)
    data = resp.json()

    if "error" in data:
        msg = _friendly_error(data["error"].get("message", "Unknown error"))
        raise AuthError(msg, data["error"].get("message", ""))

    return {
        "uid": data["localId"],
        "email": data["email"],
        "id_token": data["idToken"],
        "refresh_token": data["refreshToken"],
    }


# ── Server-side operations (Admin SDK + Firestore) ───────────


def check_user_approved(uid: str) -> bool:
    """Check if user is approved in Firestore users/{uid} doc."""
    db = get_firestore_client()
    doc = db.collection("users").document(uid).get()
    if not doc.exists:
        return False
    return doc.to_dict().get("approved", False)


def create_user_profile(uid: str, email: str) -> None:
    """Create initial user profile in Firestore with approved=False."""
    db = get_firestore_client()
    db.collection("users").document(uid).set({
        "email": email,
        "approved": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    logger.info(f"Created user profile for {email} (uid={uid})")


# ── Helpers ───────────────────────────────────────────────────


def _friendly_error(code: str) -> str:
    """Convert Firebase error codes to user-friendly messages."""
    mapping = {
        "EMAIL_EXISTS": "An account with this email already exists.",
        "INVALID_EMAIL": "Please enter a valid email address.",
        "WEAK_PASSWORD": "Password must be at least 6 characters.",
        "EMAIL_NOT_FOUND": "No account found with this email.",
        "INVALID_PASSWORD": "Incorrect password.",
        "INVALID_LOGIN_CREDENTIALS": "Invalid email or password.",
        "USER_DISABLED": "This account has been disabled.",
        "TOO_MANY_ATTEMPTS_TRY_LATER": (
            "Too many failed attempts. Please try again later."
        ),
    }
    return mapping.get(code, f"Authentication error: {code}")
