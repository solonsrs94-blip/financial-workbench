"""
Auth guard and user sidebar widget.

require_auth() — call at the top of every page to enforce login.
show_user_sidebar() — call after auth check to display user info.
"""

import streamlit as st

from config.settings import get_firebase_service_account
from lib.auth.firebase_init import init_firebase
from lib.auth.firebase_auth import check_user_approved


def _ensure_firebase() -> None:
    """Initialize Firebase once per session."""
    if st.session_state.get("_firebase_initialized"):
        return
    sa = get_firebase_service_account()
    if sa:
        init_firebase(sa)
        st.session_state["_firebase_initialized"] = True


def require_auth() -> str:
    """Block page if user is not authenticated and approved.

    Returns the uid if authenticated.
    Shows login redirect and calls st.stop() otherwise.
    """
    _ensure_firebase()

    uid = st.session_state.get("auth_uid")
    if not uid:
        st.switch_page("app.py")
        st.stop()

    if not st.session_state.get("auth_approved"):
        if check_user_approved(uid):
            st.session_state["auth_approved"] = True
        else:
            st.info(
                "Your account is pending admin approval. "
                "Please check back later."
            )
            show_user_sidebar()
            st.stop()

    return uid


def show_user_sidebar() -> None:
    """Render logged-in user info and sign-out button in sidebar."""
    email = st.session_state.get("auth_email", "")
    if not email:
        return
    with st.sidebar:
        st.caption(f"Signed in as **{email}**")
        if st.button("Sign Out", key="_auth_signout"):
            _sign_out()
            st.rerun()


def _sign_out() -> None:
    """Clear all auth-related session state keys."""
    for key in [
        "auth_uid", "auth_email", "auth_id_token",
        "auth_refresh_token", "auth_approved",
    ]:
        st.session_state.pop(key, None)
