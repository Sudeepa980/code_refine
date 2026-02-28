"""
CodeRefine – AI-powered Code Review & Optimization.
Entry point: streamlit run app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: F401

import streamlit as st
from auth.auth import is_authenticated, get_current_user, login, signup, logout
from modules.ui_components import inject_global_css

st.set_page_config(page_title="CodeRefine", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")
inject_global_css()

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None


def render_login():
    st.markdown("### Sign in")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_pw")
    if st.button("Login", use_container_width=True):
        if email and password:
            ok, err = login(email, password)
            if ok:
                st.rerun()
            else:
                st.error(err)
        else:
            st.warning("Enter email and password.")
    st.markdown("---")
    st.markdown("### Create account")
    with st.form("signup_form"):
        su_email = st.text_input("Email", key="su_email")
        su_name = st.text_input("Name (optional)", key="su_name")
        su_pw = st.text_input("Password", type="password", key="su_pw")
        if st.form_submit_button("Sign up", use_container_width=True):
            if su_email and su_pw:
                ok, err = signup(su_email, su_pw, su_name)
                if ok:
                    st.rerun()
                else:
                    st.error(err)
            else:
                st.warning("Email and password required.")


def main():
    with st.sidebar:
        st.markdown("""
<div style="text-align:center; padding:16px 0;">
    <div style="font-size:2.2rem;">⚡</div>
    <div style="font-size:1.4rem; font-weight:700; margin-top:4px;">CodeRefine</div>
    <div style="font-size:0.75rem; opacity:0.7; margin-top:2px;">AI Code Review & Optimization</div>
</div>
""", unsafe_allow_html=True)
        st.markdown("---")
        if is_authenticated():
            user = get_current_user()
            st.success(f"Hi, {user.get('name') or user.get('email', '')}")
            if st.button("Logout", use_container_width=True):
                logout()
                st.rerun()
            st.markdown("---")
            try:
                from modules.groq_client import check_key_status
                ok, msg = check_key_status()
                if ok:
                    st.caption("✅ " + msg)
                else:
                    st.caption("⚠️ " + msg)
            except Exception:
                pass
        else:
            st.info("Sign in to use all features.")
            render_login()
            st.stop()

    # Hero section
    st.markdown("""
<div style="text-align:center; padding:40px 20px 20px;">
    <div style="font-size:3rem; margin-bottom:8px;">⚡</div>
    <h1 style="font-size:2.4rem; font-weight:800; margin:0; background:linear-gradient(135deg, #6C5CE7, #A29BFE); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">CodeRefine</h1>
    <p style="font-size:1.1rem; color:#636E72; margin-top:8px; max-width:600px; margin-left:auto; margin-right:auto;">
        AI-powered code analysis, optimization, and conversion. Write better code, faster.
    </p>
</div>
""", unsafe_allow_html=True)

    # Feature cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
<div class="feature-card">
    <div class="icon">🔍</div>
    <h3>Code Review</h3>
    <p>Static analysis, error highlighting, AI explanation & bug detection with one click</p>
</div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
<div class="feature-card">
    <div class="icon">⚡</div>
    <h3>Optimization</h3>
    <p>AI-powered code optimization with complexity reduction and best practices</p>
</div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
<div class="feature-card">
    <div class="icon">🔄</div>
    <h3>Conversion</h3>
    <p>Seamless C to Python and Python to C code translation</p>
</div>""", unsafe_allow_html=True)
    with col4:
        st.markdown("""
<div class="feature-card">
    <div class="icon">⚖️</div>
    <h3>Comparison</h3>
    <p>Compare two code snippets with AI-generated diff summary</p>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats row
    try:
        from utils.db import get_type_counts, get_history
        user_id = st.session_state.get("user_id")
        if user_id:
            counts = get_type_counts(user_id)
            total = sum(counts.values())
            scored = [h["score"] for h in get_history(user_id, limit=200) if h.get("score") is not None]
            avg_score = sum(scored) // len(scored) if scored else 0

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""<div class="metric-card"><div class="metric-label">Total Analyses</div><div class="metric-value">{total}</div><div class="metric-sub">across all features</div></div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div class="metric-card"><div class="metric-label">Avg Score</div><div class="metric-value" style="color:#00B894;">{avg_score}</div><div class="metric-sub">quality score</div></div>""", unsafe_allow_html=True)
            with c3:
                opt_count = counts.get("optimized", 0) + counts.get("complexity", 0)
                st.markdown(f"""<div class="metric-card"><div class="metric-label">Optimizations</div><div class="metric-value" style="color:#E17055;">{opt_count}</div><div class="metric-sub">complexity + optimized</div></div>""", unsafe_allow_html=True)
            with c4:
                ai_count = counts.get("explanation", 0) + counts.get("bugfix", 0)
                st.markdown(f"""<div class="metric-card"><div class="metric-label">AI Insights</div><div class="metric-value" style="color:#6C5CE7;">{ai_count}</div><div class="metric-sub">explanations + bug fixes</div></div>""", unsafe_allow_html=True)
    except Exception:
        pass

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
<div style="text-align:center; padding:20px; color:#636E72; font-size:0.85rem;">
    Use the <strong>sidebar pages</strong> to get started &rarr; Code Review, Conversion, Comparison, or History
</div>
""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
