"""
Code Conversion: C ↔ Python with auto-detect and side-by-side view.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from auth.auth import is_authenticated
from modules.analyzer import detect_language
from modules.code_converter import convert_code
from modules.ui_components import inject_global_css
from utils.db import save_history

if not is_authenticated():
    st.warning("Please sign in from the main page.")
    st.stop()

st.set_page_config(page_title="Code Conversion | CodeRefine", page_icon="🔄", layout="wide")
inject_global_css()

st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
    <span style="font-size:2rem;">🔄</span>
    <div>
        <div style="font-size:1.6rem; font-weight:800; color:#2D3436;">Code Conversion</div>
        <div style="font-size:0.85rem; color:#636E72;">Auto-detect source language &middot; Seamless C ↔ Python translation</div>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

col_from, col_arrow, col_to = st.columns([2, 0.5, 2])

with col_from:
    code = st.text_area("Source code (language auto-detected)", height=320, key="conv_code", placeholder="Paste your code here — language is detected automatically...")

    if code.strip():
        detected = detect_language(code)
        from_lang = detected
        to_lang = "python" if from_lang == "c" else "c"
        from_label = "🐍 Python" if from_lang == "python" else "⚙️ C"
        to_label = "🐍 Python" if to_lang == "python" else "⚙️ C"
        st.markdown(f"""
<div style="display:inline-flex; align-items:center; gap:8px; background:#F8F9FA; padding:6px 16px; border-radius:8px; border:1px solid #EDF2F7;">
    <span style="font-size:0.85rem; color:#636E72;">Detected:</span>
    <span style="font-size:0.9rem; font-weight:700; color:#6C5CE7;">{from_label}</span>
    <span style="color:#636E72;">→</span>
    <span style="font-size:0.9rem; font-weight:700; color:#00B894;">{to_label}</span>
</div>
""", unsafe_allow_html=True)
    else:
        from_lang = "c"
        to_lang = "python"

with col_arrow:
    st.markdown(f"""
<div style="display:flex; align-items:center; justify-content:center; height:380px;">
    <div style="text-align:center;">
        <div style="font-size:2.5rem; color:#6C5CE7;">→</div>
        <div style="font-size:0.75rem; color:#636E72; font-weight:600; margin-top:4px;">auto<br>convert</div>
    </div>
</div>
""", unsafe_allow_html=True)

with col_to:
    st.markdown(f"**Target: {to_lang.upper()}**")
    output_area = st.empty()
    output_area.text_area("Converted code", value="", height=320, disabled=True, key="conv_output_ph")

convert_btn = st.button("🔄  Convert", type="primary", use_container_width=True)

if convert_btn:
    if not code.strip():
        st.warning("Paste code first.")
    else:
        with st.spinner("Converting..."):
            out, err = convert_code(code, from_lang, to_lang)
        if err:
            st.error(err)
        elif out:
            with col_to:
                output_area.empty()
                st.code(out, language=to_lang)
            try:
                save_history(st.session_state["user_id"], "conversion", language_from=from_lang, language_to=to_lang, code_input=code, code_output=out)
            except Exception:
                pass
            st.download_button(
                "📥 Download converted code",
                data=out,
                file_name=f"converted.{'py' if to_lang=='python' else 'c'}",
                mime="text/plain",
                use_container_width=True,
            )
        else:
            st.error("No response. Check your GROQ_API_KEY.")
