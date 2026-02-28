"""
Code Review — modular feature selection via sidebar checkboxes.
Each feature runs independently, saves its own history entry.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from auth.auth import is_authenticated
from modules.analyzer import analyze_static, analyze_complexity, detect_language
from modules.quality_score import compute_quality_score
from modules.ai_explainer import explain_line_by_line
from modules.ai_bug_fix import detect_bugs_and_suggest_fixes
from modules.ai_optimizer import optimize_code, suggest_alternative_approach
from modules.report_pdf import generate_pdf
from modules.ui_components import (
    inject_global_css, render_highlighted_code, render_score_gauge,
    render_complexity_visual, render_metric_card, render_complexity_chart,
)
from utils.db import save_history

if not is_authenticated():
    st.warning("Please sign in from the main page.")
    st.stop()

st.set_page_config(page_title="Code Review | CodeRefine", page_icon="🔍", layout="wide")
inject_global_css()

# ═══════════════════════════════════
#    SIDEBAR: Feature Checkboxes
# ═══════════════════════════════════
with st.sidebar:
    st.markdown("""
<div style="padding:12px 0 4px;">
    <div style="font-size:1rem; font-weight:700; color:#A29BFE;">🛠 Analysis Features</div>
    <div style="font-size:0.72rem; color:#B2BEC3; margin-top:2px;">Select what to run on your code</div>
</div>
""", unsafe_allow_html=True)

    feat_complexity = st.checkbox("⏱  Time & Space Complexity", value=True, key="feat_complexity")
    feat_quality    = st.checkbox("💯  Quality Score", value=True, key="feat_quality")
    feat_optimize   = st.checkbox("⚡  Optimized Solution", value=True, key="feat_optimize")
    feat_explain    = st.checkbox("🧠  AI Explanation", value=False, key="feat_explain")
    feat_bugfix     = st.checkbox("🐛  Bug Fix Suggestions", value=False, key="feat_bugfix")
    feat_alt        = st.checkbox("🔀  Alternative Approach", value=False, key="feat_alt")

    st.markdown("---")
    st.markdown("""
<div style="font-size:0.72rem; color:#B2BEC3;">
    Each feature runs independently and saves to History with its own type.
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════
#    MAIN: Header + Code Input
# ═══════════════════════════════════
st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
    <span style="font-size:2rem;">🔍</span>
    <div>
        <div style="font-size:1.6rem; font-weight:800; color:#2D3436;">Code Review</div>
        <div style="font-size:0.85rem; color:#636E72;">Select features in sidebar &middot; Auto-detect language &middot; Run what you need</div>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

code = st.text_area(
    "Paste your code (language auto-detected)",
    height=240,
    key="review_code",
    placeholder="Paste any C or Python code here — language is detected automatically...",
)

# Live language detection
lang = "python"
if code.strip():
    detected = detect_language(code)
    lang_icon = "🐍" if detected == "python" else "⚙️"
    lang_name = "Python" if detected == "python" else "C"
    st.markdown(f"""
<div style="display:inline-flex; align-items:center; gap:8px; background:#F8F9FA; padding:6px 16px; border-radius:8px; border:1px solid #EDF2F7; margin-bottom:8px;">
    <span style="font-size:0.85rem; color:#636E72;">Detected:</span>
    <span style="font-size:0.9rem; font-weight:700; color:#6C5CE7;">{lang_icon} {lang_name}</span>
</div>
""", unsafe_allow_html=True)
    col_ov, _ = st.columns([1, 3])
    with col_ov:
        override = st.selectbox("Override?", ["Auto-detect", "python", "c"], key="lang_ov", label_visibility="collapsed")
    lang = detected if override == "Auto-detect" else override


# ═══════════════════════════════════
#    SELECTED FEATURES SUMMARY
# ═══════════════════════════════════
selected = []
if feat_complexity: selected.append("⏱ Complexity")
if feat_quality:    selected.append("💯 Quality")
if feat_optimize:   selected.append("⚡ Optimize")
if feat_explain:    selected.append("🧠 Explain")
if feat_bugfix:     selected.append("🐛 Bug Fix")
if feat_alt:        selected.append("🔀 Alternative")

if selected:
    pills = " ".join(f'<span class="badge badge-info" style="margin:2px;">{s}</span>' for s in selected)
    st.markdown(f'<div style="margin:8px 0;">{pills}</div>', unsafe_allow_html=True)
else:
    st.info("Select at least one feature from the sidebar.")


# ═══════════════════════════════════
#    PER-FEATURE EXECUTION BUTTONS
# ═══════════════════════════════════
if code.strip() and selected:
    st.markdown("---")

    # Always run static analysis (needed by quality & bugfix)
    static_issues = analyze_static(lang, code)

    # Row of buttons
    btn_cols = st.columns(len(selected))
    triggers = {}
    for i, s in enumerate(selected):
        with btn_cols[i]:
            key_name = s.split(" ", 1)[1].lower().replace(" ", "_")
            triggers[key_name] = st.button(f"{s}", key=f"btn_{key_name}", use_container_width=True, type="primary")

    st.markdown("<br>", unsafe_allow_html=True)
    user_id = st.session_state.get("user_id")

    # ─── COMPLEXITY ───
    if triggers.get("complexity"):
        with st.spinner("Analyzing complexity..."):
            time_c, space_c, time_reasons, space_reasons = analyze_complexity(lang, code)

        save_history(user_id, "complexity", language_from=lang, code_input=code,
                     report_json={"time_complexity": time_c, "space_complexity": space_c,
                                  "time_reasons": time_reasons, "space_reasons": space_reasons})

        st.markdown('<div class="section-header">⏱ Time & Space Complexity</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1.5])
        with c1:
            st.markdown(render_complexity_visual(time_c, space_c, time_reasons, space_reasons), unsafe_allow_html=True)
        with c2:
            fig = render_complexity_chart(time_c, space_c)
            st.plotly_chart(fig, use_container_width=True)

    # ─── QUALITY SCORE ───
    if triggers.get("quality"):
        with st.spinner("Computing quality score..."):
            time_c2, space_c2, _, _ = analyze_complexity(lang, code)
            has_syntax = any(i.get("type") == "syntax_error" for i in static_issues)
            score, score_reasons = compute_quality_score(static_issues, time_c2, space_c2, has_syntax)

        save_history(user_id, "quality", language_from=lang, code_input=code, score=score,
                     report_json={"score": score, "reasons": score_reasons,
                                  "issues_count": len(static_issues)})

        st.markdown('<div class="section-header">💯 Quality Score</div>', unsafe_allow_html=True)
        q1, q2, q3 = st.columns([1, 1.2, 1.2])
        with q1:
            st.markdown(render_score_gauge(score), unsafe_allow_html=True)
        with q2:
            st.markdown("##### Score Breakdown")
            for r in score_reasons:
                st.markdown(f"- {r}")
        with q3:
            st.markdown("##### Code with Errors")
            st.markdown(render_highlighted_code(code, static_issues, lang), unsafe_allow_html=True)

    # ─── OPTIMIZED SOLUTION ───
    if triggers.get("optimize"):
        with st.spinner("Generating optimized solution..."):
            time_c3, _, _, _ = analyze_complexity(lang, code)
            issues_summary = "; ".join(i.get("message", "") for i in static_issues[:8])
            optimized, opt_err = optimize_code(code, lang, time_c3, issues_summary)

        if optimized:
            save_history(user_id, "optimized", language_from=lang, code_input=code,
                         code_output=optimized, report_json={"original_complexity": time_c3})
        st.markdown('<div class="section-header">⚡ Optimized Solution</div>', unsafe_allow_html=True)
        if opt_err:
            st.error(opt_err)
        elif optimized:
            col_orig, col_opt = st.columns(2)
            with col_orig:
                st.markdown("""<div style="background:#E17055; color:white; padding:8px 14px; border-radius:8px 8px 0 0; font-weight:600; font-size:0.85rem;">ORIGINAL</div>""", unsafe_allow_html=True)
                st.code(code, language=lang)
            with col_opt:
                st.markdown("""<div style="background:#00B894; color:white; padding:8px 14px; border-radius:8px 8px 0 0; font-weight:600; font-size:0.85rem;">OPTIMIZED</div>""", unsafe_allow_html=True)
                st.markdown(optimized)

    # ─── AI EXPLANATION ───
    if triggers.get("explain"):
        with st.spinner("AI explaining your code line-by-line..."):
            explanation, exp_err = explain_line_by_line(code, lang)

        if explanation:
            save_history(user_id, "explanation", language_from=lang, code_input=code,
                         report_json={"explanation": explanation})
        st.markdown('<div class="section-header">🧠 AI Explanation</div>', unsafe_allow_html=True)
        if exp_err:
            st.error(exp_err)
        elif explanation:
            st.markdown(explanation)

    # ─── BUG FIX ───
    if triggers.get("bug_fix"):
        with st.spinner("Detecting bugs and suggesting fixes..."):
            bugs, bug_err = detect_bugs_and_suggest_fixes(code, lang, static_issues)

        if bugs:
            save_history(user_id, "bugfix", language_from=lang, code_input=code,
                         report_json={"bugs": bugs, "static_issues": static_issues})
        st.markdown('<div class="section-header">🐛 Bug Detection & Fixes</div>', unsafe_allow_html=True)

        # Show highlighted code first
        if static_issues:
            st.markdown(render_highlighted_code(code, static_issues, lang), unsafe_allow_html=True)
            st.markdown("")

        if bug_err:
            st.error(bug_err)
        elif bugs:
            st.markdown(bugs)

    # ─── ALTERNATIVE APPROACH ───
    if triggers.get("alternative"):
        with st.spinner("Finding alternative approaches..."):
            alt, alt_err = suggest_alternative_approach(code, lang)

        if alt:
            save_history(user_id, "alternative", language_from=lang, code_input=code,
                         report_json={"alternative": alt})
        st.markdown('<div class="section-header">🔀 Alternative Approach</div>', unsafe_allow_html=True)
        if alt_err:
            st.error(alt_err)
        elif alt:
            st.markdown(alt)

    # ─── RUN ALL SELECTED ───
    st.markdown("---")
    any_triggered = any(triggers.values())
    if not any_triggered:
        st.markdown("""
<div style="text-align:center; padding:30px; color:#636E72; background:#F8F9FA; border-radius:12px;">
    <div style="font-size:1.5rem; margin-bottom:8px;">👆</div>
    <div style="font-size:0.95rem; font-weight:600;">Click any button above to run that feature</div>
    <div style="font-size:0.8rem; margin-top:4px;">Each result is saved separately to your History</div>
</div>
""", unsafe_allow_html=True)

    # PDF for full review
    if any_triggered:
        st.markdown("<br>", unsafe_allow_html=True)
        c_l, c_m, c_r = st.columns([2, 1, 2])
        with c_m:
            time_c_pdf, space_c_pdf, tr_pdf, sr_pdf = analyze_complexity(lang, code)
            has_syn = any(i.get("type") == "syntax_error" for i in static_issues)
            sc_pdf, scr_pdf = compute_quality_score(static_issues, time_c_pdf, space_c_pdf, has_syn)
            pdf_buf = generate_pdf(code, lang, static_issues, time_c_pdf, space_c_pdf, tr_pdf, sr_pdf, sc_pdf, scr_pdf, None, None)
            if pdf_buf:
                st.download_button("📄 Download PDF", data=pdf_buf.getvalue(), file_name="coderefine_report.pdf",
                                   mime="application/pdf", use_container_width=True)

elif not code.strip():
    st.markdown("""
<div style="text-align:center; padding:50px 20px; color:#636E72;">
    <div style="font-size:3rem; margin-bottom:12px;">📋</div>
    <div style="font-size:1.1rem; font-weight:600;">Paste your code above to get started</div>
    <div style="font-size:0.85rem; margin-top:4px;">Select features from the sidebar, then click to run each one</div>
</div>
""", unsafe_allow_html=True)
