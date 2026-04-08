"""
Auth guard and user sidebar widget.

require_auth() — call at the top of every page to enforce login.
show_user_sidebar() — call after auth check to display user info.
"""

import logging

import streamlit as st

from config.settings import get_firebase_service_account, FIREBASE_API_KEY
from lib.auth.firebase_init import init_firebase
from lib.auth.firebase_auth import check_user_approved, refresh_id_token, AuthError

logger = logging.getLogger(__name__)


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
    _try_refresh_token()

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
        _render_autosave_controls()


def _render_autosave_controls() -> None:
    """Manual save/restore buttons for the current ticker's autosave."""
    ticker = (
        st.session_state.get("_val_cached_ticker")
        or st.query_params.get("ticker", "")
    )
    if not ticker:
        return
    ticker = ticker.upper()
    from lib.storage.autosave import (
        write_autosave, delete_autosave,
        autosave_age_seconds, format_age, read_autosave,
    )
    from lib.exports.session_restorer import restore_valuation_state

    st.divider()
    st.caption(f"Session — {ticker}")
    age = autosave_age_seconds(ticker)
    if age is not None:
        st.caption(f"Autosave: {format_age(age)}")

    if st.button("💾 Save session now", key="_autosave_manual"):
        if write_autosave(dict(st.session_state), ticker):
            st.toast(f"Session saved for {ticker}")
        else:
            st.toast("Save failed")

    if age is not None:
        if st.button("📂 Restore autosave", key="_autosave_manual_restore"):
            payload = read_autosave(ticker)
            if payload:
                state, _ = restore_valuation_state(payload)
                for k, v in state.items():
                    st.session_state[k] = v
                st.session_state[f"_autosave_checked_{ticker}"] = True
                st.rerun()
        if st.button("🗑 Clear autosave", key="_autosave_manual_clear"):
            delete_autosave(ticker)
            st.toast(f"Cleared autosave for {ticker}")
            st.rerun()


def _try_refresh_token() -> None:
    """Verify the stored ID token; refresh it if expired.

    Silent on success. On unrecoverable failure, clears auth so that
    require_auth() bounces the user to login — but only after the
    refresh attempt fails, so live sessions are preserved across the
    1-hour token expiry window.
    """
    id_token = st.session_state.get("auth_id_token")
    refresh_tok = st.session_state.get("auth_refresh_token")
    if not id_token or not refresh_tok:
        return
    try:
        from firebase_admin import auth as fb_auth
        try:
            fb_auth.verify_id_token(id_token, check_revoked=False)
            return  # still valid
        except fb_auth.ExpiredIdTokenError:
            logger.info("ID token expired; attempting refresh")
        except fb_auth.RevokedIdTokenError:
            logger.warning("ID token revoked; signing out")
            _sign_out()
            return
        except Exception as exc:
            # Unknown verify error — preserve session, log and bail
            logger.warning("Token verify raised %s: %s", type(exc).__name__, exc)
            return
    except Exception as exc:
        logger.warning("firebase_admin import failed: %s", exc)
        return

    if not FIREBASE_API_KEY:
        logger.warning("FIREBASE_API_KEY missing; cannot refresh token")
        return
    try:
        result = refresh_id_token(refresh_tok, FIREBASE_API_KEY)
        if result.get("id_token"):
            st.session_state["auth_id_token"] = result["id_token"]
            st.session_state["auth_refresh_token"] = result.get(
                "refresh_token", refresh_tok
            )
            logger.info("ID token refreshed successfully")
        else:
            logger.warning("Refresh returned no id_token; keeping session")
    except AuthError as exc:
        logger.warning("Refresh failed (%s); signing out", exc)
        _sign_out()
    except Exception as exc:
        # Network blip, JSON decode error, etc. — do NOT sign out
        logger.warning(
            "Refresh raised %s: %s; keeping session",
            type(exc).__name__, exc,
        )


def _sign_out() -> None:
    """Clear all auth-related session state keys."""
    for key in [
        "auth_uid", "auth_email", "auth_id_token",
        "auth_refresh_token", "auth_approved",
    ]:
        st.session_state.pop(key, None)
