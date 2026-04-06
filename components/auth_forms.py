"""
Login and sign-up forms for Firebase Email/Password auth.
"""

import streamlit as st

from config.settings import FIREBASE_API_KEY
from lib.auth.firebase_auth import sign_in, sign_up, create_user_profile, AuthError


def render_auth_page() -> None:
    """Render login / sign-up page with tab toggle."""
    tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])

    with tab_login:
        _render_login_form()

    with tab_signup:
        _render_signup_form()


def _render_login_form() -> None:
    """Email + password sign-in form."""
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In", type="primary")

    if submitted and email and password:
        try:
            result = sign_in(email, password, FIREBASE_API_KEY)
            st.session_state["auth_uid"] = result["uid"]
            st.session_state["auth_email"] = result["email"]
            st.session_state["auth_id_token"] = result["id_token"]
            st.session_state["auth_refresh_token"] = result["refresh_token"]
            st.rerun()
        except AuthError as e:
            st.error(e.message)


def _render_signup_form() -> None:
    """Email + password sign-up form with confirmation."""
    with st.form("signup_form"):
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pw")
        password2 = st.text_input(
            "Confirm Password", type="password", key="signup_pw2"
        )
        submitted = st.form_submit_button("Create Account")

    if submitted:
        if not email or not password:
            st.error("Please fill in all fields.")
            return
        if password != password2:
            st.error("Passwords do not match.")
            return
        if len(password) < 6:
            st.error("Password must be at least 6 characters.")
            return
        try:
            result = sign_up(email, password, FIREBASE_API_KEY)
            create_user_profile(result["uid"], result["email"])
            st.success(
                "Account created! Waiting for admin approval. "
                "You'll be able to sign in once approved."
            )
        except AuthError as e:
            st.error(e.message)
