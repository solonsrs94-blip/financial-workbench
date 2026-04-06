"""
Firebase Admin SDK initialization. Pure Python — NO streamlit imports.

Singleton pattern: init_firebase() called once at app startup,
then get_firestore_client() / get_auth_module() used everywhere.
"""

import firebase_admin
from firebase_admin import credentials, firestore, auth

_app = None


def init_firebase(service_account=None):
    """Initialize Firebase Admin SDK (singleton).

    Args:
        service_account: Service account credentials dict.
            If None, uses Application Default Credentials.
    """
    global _app
    if _app is not None:
        return _app

    # Check if already initialized (e.g. Streamlit re-run)
    try:
        _app = firebase_admin.get_app()
        return _app
    except ValueError:
        pass

    if service_account:
        cred = credentials.Certificate(service_account)
    else:
        cred = credentials.ApplicationDefault()

    try:
        _app = firebase_admin.initialize_app(cred)
    except ValueError:
        # Already initialized by another thread/re-run
        _app = firebase_admin.get_app()
    return _app


def get_firestore_client():
    """Return Firestore client. Firebase must be initialized first."""
    if not firebase_admin._apps:
        raise RuntimeError(
            "Firebase not initialized. Call init_firebase() first."
        )
    return firestore.client()


def get_auth_module():
    """Return firebase_admin.auth module for server-side user management."""
    if not firebase_admin._apps:
        raise RuntimeError(
            "Firebase not initialized. Call init_firebase() first."
        )
    return auth
