"""
Code Comparison: two snippets side-by-side with AI summary.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from auth.auth import is_authenticated
from modules.code_comparison import compare_and_summarize
from modules.ui_components import inject_global_css
from utils.db import save_history

if not is_authenticated():
    st.warning("Please sign in from the main page.")
    st.stop()

st.set_page_config(page_title="Code Comparison | CodeRefine", page_icon="⚖️", layout="wide")
inject_global_css()

st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
    <span style="font-size:2rem;">⚖️</span>
    <div>
        <div style="font-size:1.6rem; font-weight:800; color:#2D3436;">Code Comparison</div>
        <div style="font-size:0.85rem; color:#636E72;">Compare two code snippets with AI-generated diff summary</div>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""<div style="background:#6C5CE7; color:white; padding:8px 16px; border-radius:8px 8px 0 0; font-weight:600; font-size:0.9rem;">Snippet A</div>""", unsafe_allow_html=True)
    label_a = st.text_input("Label", value="Code A", key="comp_label_a", label_visibility="collapsed")
    code_a = st.text_area("Code A", height=280, key="comp_code_a", placeholder="Paste first snippet...", label_visibility="collapsed")
with col2:
    st.markdown("""<div style="background:#00B894; color:white; padding:8px 16px; border-radius:8px 8px 0 0; font-weight:600; font-size:0.9rem;">Snippet B</div>""", unsafe_allow_html=True)
    label_b = st.text_input("Label", value="Code B", key="comp_label_b", label_visibility="collapsed")
    code_b = st.text_area("Code B", height=280, key="comp_code_b", placeholder="Paste second snippet...", label_visibility="collapsed")

compare_btn = st.button("⚖️  Compare", type="primary", use_container_width=True)

if compare_btn:
    if not code_a.strip() or not code_b.strip():
        st.warning("Paste both snippets.")
    else:
        with st.spinner("Comparing with AI..."):
            summary, err = compare_and_summarize(code_a, code_b, label_a=label_a, label_b=label_b)
        if err:
            st.error(err)
        elif summary:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
<div style="background:white; border-radius:16px; padding:24px; box-shadow:0 2px 16px rgba(0,0,0,0.06); border:1px solid #EDF2F7;">
    <div style="font-size:1.1rem; font-weight:700; color:#2D3436; margin-bottom:16px;">🔍 Differences (AI Summary)</div>
""", unsafe_allow_html=True)
            st.markdown(summary)
            st.markdown("</div>", unsafe_allow_html=True)

            # Quick stats
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""<div class="metric-card"><div class="metric-label">Snippet A</div><div class="metric-value" style="color:#6C5CE7;">{len(code_a.splitlines())}</div><div class="metric-sub">lines</div></div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div class="metric-card"><div class="metric-label">Snippet B</div><div class="metric-value" style="color:#00B894;">{len(code_b.splitlines())}</div><div class="metric-sub">lines</div></div>""", unsafe_allow_html=True)
            with c3:
                diff = abs(len(code_a.splitlines()) - len(code_b.splitlines()))
                st.markdown(f"""<div class="metric-card"><div class="metric-label">Difference</div><div class="metric-value" style="color:#E17055;">{diff}</div><div class="metric-sub">lines</div></div>""", unsafe_allow_html=True)

            try:
                save_history(
                    st.session_state["user_id"], "comparison",
                    code_input=code_a[:5000], code_output=code_b[:5000],
                    report_json={"label_a": label_a, "label_b": label_b, "summary": summary},
                )
            except Exception:
                pass
        else:
            st.error("No response. Check your GROQ_API_KEY.")
