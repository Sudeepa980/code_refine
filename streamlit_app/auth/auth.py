"""
Streamlit authentication: login, signup, logout, session handling.
"""
import streamlit as st

from .db import create_user, check_password, get_user_by_id


def is_authenticated() -> bool:
    return bool(st.session_state.get("user_id"))


def get_current_user():
    if not st.session_state.get("user_id"):
        return None
    return get_user_by_id(st.session_state["user_id"])


def login(email: str, password: str) -> tuple:
    """Returns (True, None) or (False, error_message)."""
    user = check_password(email, password)
    if user:
        st.session_state["user_id"] = user["id"]
        st.session_state["user_email"] = user["email"]
        st.session_state["user_name"] = user.get("name") or user["email"]
        return (True, None)
    return (False, "Invalid email or password.")


def signup(email: str, password: str, name: str = "") -> tuple:
    """Returns (True, None) or (False, error_message)."""
    if len(password) < 6:
        return (False, "Password must be at least 6 characters.")
    user_id, err = create_user(email, password, name)
    if err:
        return (False, err)
    user = get_user_by_id(user_id)
    st.session_state["user_id"] = user["id"]
    st.session_state["user_email"] = user["email"]
    st.session_state["user_name"] = user.get("name") or user["email"]
    return (True, None)


def logout():
    for key in ("user_id", "user_email", "user_name"):
        if key in st.session_state:
            del st.session_state[key]
