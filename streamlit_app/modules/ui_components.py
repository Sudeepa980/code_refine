"""
Shared UI components: CSS theme, code highlighter, score gauge, metric cards, charts.
"""
import html
import math
import streamlit as st
import plotly.graph_objects as go
from typing import List, Dict, Optional


def inject_global_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --accent: #6C5CE7;
    --accent-light: #A29BFE;
    --success: #00B894;
    --warning: #FDCB6E;
    --danger: #E17055;
    --bg-card: #FFFFFF;
    --bg-dark: #2D3436;
    --text-primary: #2D3436;
    --text-secondary: #636E72;
    --border: #DFE6E9;
    --shadow: 0 2px 16px rgba(108,92,231,0.08);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2D3436 0%, #1E272E 100%);
}
section[data-testid="stSidebar"] * {
    color: #DFE6E9 !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
}

.metric-card {
    background: var(--bg-card);
    border-radius: 16px;
    padding: 24px;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(108,92,231,0.15);
}
.metric-card .metric-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: var(--accent);
    margin: 8px 0 4px;
}
.metric-card .metric-label {
    font-size: 0.85rem;
    color: var(--text-secondary);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.metric-card .metric-sub {
    font-size: 0.78rem;
    color: var(--text-secondary);
    margin-top: 4px;
}

.feature-card {
    background: var(--bg-card);
    border-radius: 16px;
    padding: 28px 24px;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
    min-height: 180px;
}
.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(108,92,231,0.18);
}
.feature-card .icon { font-size: 2.5rem; margin-bottom: 12px; }
.feature-card h3 { font-size: 1.1rem; font-weight: 600; color: var(--text-primary); margin: 0 0 8px; }
.feature-card p { font-size: 0.85rem; color: var(--text-secondary); margin: 0; line-height: 1.5; }

.section-header {
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 32px 0 16px;
    padding-bottom: 8px;
    border-bottom: 3px solid var(--accent);
    display: inline-block;
}

.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.3px;
}
.badge-danger { background: #FFEAA7; color: #D63031; }
.badge-warning { background: #FFF3E0; color: #E17055; }
.badge-success { background: #E8F5E9; color: #00B894; }
.badge-info { background: #E8EAF6; color: #6C5CE7; }

.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px 10px 0 0;
    font-weight: 600;
}

/* ── Chat-like History ── */
.chat-container {
    max-width: 900px;
    margin: 0 auto;
}
.chat-msg {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
    animation: fadeIn 0.3s ease;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
.chat-msg .avatar {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    flex-shrink: 0;
}
.chat-msg .bubble {
    background: var(--bg-card);
    border-radius: 0 16px 16px 16px;
    padding: 16px 20px;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    flex: 1;
    min-width: 0;
}
.chat-msg .bubble .bubble-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
}
.chat-msg .bubble .bubble-title {
    font-weight: 700;
    font-size: 0.95rem;
    color: var(--text-primary);
}
.chat-msg .bubble .bubble-time {
    font-size: 0.72rem;
    color: var(--text-secondary);
}
.chat-msg .bubble .bubble-body {
    font-size: 0.85rem;
    color: var(--text-primary);
    line-height: 1.6;
}
.chat-msg .bubble .bubble-footer {
    display: flex;
    gap: 8px;
    margin-top: 12px;
    padding-top: 8px;
    border-top: 1px solid #F0F0F0;
}
.history-sidebar-item {
    padding: 10px 14px;
    border-radius: 10px;
    cursor: pointer;
    transition: background 0.15s;
    border: 1px solid transparent;
    margin-bottom: 4px;
}
.history-sidebar-item:hover {
    background: #F8F9FA;
    border-color: var(--border);
}
.history-sidebar-item.active {
    background: #EDE7F6;
    border-color: var(--accent-light);
}
.history-sidebar-item .item-title {
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.history-sidebar-item .item-meta {
    font-size: 0.7rem;
    color: var(--text-secondary);
    margin-top: 2px;
}
.type-pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.3px;
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)


def render_highlighted_code(code: str, issues: List[Dict], language: str = "c") -> str:
    """Render code as HTML with error lines highlighted and annotated."""
    lines = code.splitlines()
    error_map = {}
    for iss in issues:
        ln = iss.get("line")
        if ln and 1 <= ln <= len(lines):
            if ln not in error_map:
                error_map[ln] = []
            error_map[ln].append(iss)

    lang_class = "python" if language == "python" else "c"

    html_parts = [f"""
<div style="background:#1E1E2E; border-radius:12px; overflow:hidden; font-family:'JetBrains Mono',monospace; font-size:13px; box-shadow:0 4px 24px rgba(0,0,0,0.2); margin:8px 0;">
<div style="background:#181825; padding:8px 16px; display:flex; align-items:center; gap:8px; border-bottom:1px solid #313244;">
    <span style="width:12px;height:12px;border-radius:50%;background:#E17055;display:inline-block;"></span>
    <span style="width:12px;height:12px;border-radius:50%;background:#FDCB6E;display:inline-block;"></span>
    <span style="width:12px;height:12px;border-radius:50%;background:#00B894;display:inline-block;"></span>
    <span style="color:#6C7086; font-size:12px; margin-left:8px;">{lang_class.upper()} &middot; {len(lines)} lines &middot; {len(error_map)} issue(s)</span>
</div>
<div style="overflow-x:auto; padding:0;">
"""]

    for i, line in enumerate(lines, 1):
        escaped = html.escape(line) if line else "&nbsp;"
        if i in error_map:
            severity = "syntax_error" if any(e.get("type") == "syntax_error" for e in error_map[i]) else "warning"
            bg = "rgba(225,112,85,0.15)" if severity == "syntax_error" else "rgba(253,203,110,0.12)"
            border_color = "#E17055" if severity == "syntax_error" else "#FDCB6E"
            msgs = "; ".join(e.get("message", "") for e in error_map[i])
            tooltip = html.escape(msgs)
            html_parts.append(
                f'<div style="display:flex; border-left:3px solid {border_color}; background:{bg};" title="{tooltip}">'
                f'<span style="min-width:48px; padding:2px 12px 2px 8px; color:#E17055; text-align:right; user-select:none; font-size:12px; line-height:22px;">{i}</span>'
                f'<span style="flex:1; padding:2px 16px 2px 0; color:#CDD6F4; white-space:pre; line-height:22px;">{escaped}</span>'
                f'<span style="padding:2px 12px; color:{border_color}; font-size:11px; white-space:nowrap; line-height:22px; opacity:0.9;">&larr; {tooltip}</span>'
                f'</div>'
            )
        else:
            html_parts.append(
                f'<div style="display:flex;">'
                f'<span style="min-width:48px; padding:2px 12px 2px 8px; color:#6C7086; text-align:right; user-select:none; font-size:12px; line-height:22px;">{i}</span>'
                f'<span style="flex:1; padding:2px 16px 2px 0; color:#CDD6F4; white-space:pre; line-height:22px;">{escaped}</span>'
                f'</div>'
            )

    html_parts.append("</div></div>")
    return "\n".join(html_parts)


def render_score_gauge(score: int) -> str:
    """Render a circular quality score gauge as HTML/CSS."""
    if score >= 80:
        color = "#00B894"
        label = "Excellent"
    elif score >= 60:
        color = "#6C5CE7"
        label = "Good"
    elif score >= 40:
        color = "#FDCB6E"
        label = "Fair"
    else:
        color = "#E17055"
        label = "Needs Work"

    deg = int(score * 3.6)

    return f"""
<div style="display:flex; flex-direction:column; align-items:center; padding:20px;">
    <div style="position:relative; width:160px; height:160px;">
        <svg viewBox="0 0 160 160" style="transform:rotate(-90deg);">
            <circle cx="80" cy="80" r="70" fill="none" stroke="#2D3436" stroke-width="12" opacity="0.1"/>
            <circle cx="80" cy="80" r="70" fill="none" stroke="{color}" stroke-width="12"
                stroke-dasharray="{score * 4.4} {440 - score * 4.4}"
                stroke-linecap="round"
                style="transition: stroke-dasharray 1s ease;"/>
        </svg>
        <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); text-align:center;">
            <div style="font-size:2.5rem; font-weight:700; color:{color}; line-height:1;">{score}</div>
            <div style="font-size:0.7rem; color:#636E72; font-weight:600; margin-top:2px;">/ 100</div>
        </div>
    </div>
    <div style="margin-top:8px; font-size:0.9rem; font-weight:600; color:{color};">{label}</div>
</div>
"""


def render_complexity_visual(time_c: str, space_c: str, time_reasons: List[Dict], space_reasons: List[Dict]) -> str:
    """Render complexity as a visual card."""
    complexity_levels = {"O(1)": 1, "O(log n)": 2, "O(n)": 3, "O(n log n)": 4, "O(n²)": 5, "O(n³) or higher": 6, "O(n³)+": 6}
    time_level = complexity_levels.get(time_c, 3)
    space_level = complexity_levels.get(space_c, 3)

    def bar(level, label, value, color):
        pct = int(level / 6 * 100)
        return f"""
<div style="margin:12px 0;">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
        <span style="font-size:0.85rem; font-weight:600; color:#2D3436;">{label}</span>
        <span style="font-size:1rem; font-weight:700; color:{color};">{value}</span>
    </div>
    <div style="background:#EDF2F7; border-radius:8px; height:12px; overflow:hidden;">
        <div style="background:linear-gradient(90deg, {color}, {color}aa); width:{pct}%; height:100%; border-radius:8px; transition:width 1s ease;"></div>
    </div>
</div>"""

    time_color = "#00B894" if time_level <= 2 else "#6C5CE7" if time_level <= 4 else "#E17055"
    space_color = "#00B894" if space_level <= 2 else "#6C5CE7" if space_level <= 4 else "#E17055"

    reasons_html = ""
    if time_reasons:
        reasons_html += '<div style="margin-top:16px;">'
        for r in time_reasons[:6]:
            reasons_html += f'<div style="padding:6px 0; font-size:0.82rem; color:#636E72; border-bottom:1px solid #F0F0F0;">Line {r.get("line", "?")} &mdash; {html.escape(r.get("reason", ""))} &rarr; <strong>{html.escape(r.get("contribution", ""))}</strong></div>'
        reasons_html += "</div>"

    return f"""
<div style="background:white; border-radius:16px; padding:24px; box-shadow:0 2px 16px rgba(0,0,0,0.06); border:1px solid #EDF2F7;">
    <div style="font-size:1rem; font-weight:700; color:#2D3436; margin-bottom:16px;">Complexity Analysis</div>
    {bar(time_level, "⏱ Time", time_c, time_color)}
    {bar(space_level, "💾 Space", space_c, space_color)}
    {reasons_html}
</div>
"""


def render_metric_card(value: str, label: str, sub: str = "", color: str = "#6C5CE7") -> str:
    return f"""
<div class="metric-card">
    <div class="metric-label">{label}</div>
    <div class="metric-value" style="color:{color};">{value}</div>
    <div class="metric-sub">{sub}</div>
</div>
"""


def render_complexity_chart(time_c: str, space_c: str) -> go.Figure:
    """
    Plotly chart showing all complexity classes as growth curves,
    with the current code's time & space complexity highlighted.
    """
    n_vals = list(range(1, 51))

    curves = {
        "O(1)":        [1] * len(n_vals),
        "O(log n)":    [max(1, math.log2(n)) for n in n_vals],
        "O(n)":        [n for n in n_vals],
        "O(n log n)":  [n * max(1, math.log2(n)) for n in n_vals],
        "O(n²)":       [n**2 for n in n_vals],
        "O(n³)":       [n**3 for n in n_vals],
    }

    complexity_aliases = {
        "O(n³) or higher": "O(n³)", "O(n³)+": "O(n³)",
        "O(n²)": "O(n²)", "O(n log n)": "O(n log n)",
        "O(n)": "O(n)", "O(log n)": "O(log n)", "O(1)": "O(1)",
    }
    time_match = complexity_aliases.get(time_c, time_c)
    space_match = complexity_aliases.get(space_c, space_c)

    colors = {
        "O(1)": "#00B894",
        "O(log n)": "#00CEC9",
        "O(n)": "#6C5CE7",
        "O(n log n)": "#FDCB6E",
        "O(n²)": "#E17055",
        "O(n³)": "#D63031",
    }

    fig = go.Figure()

    for label, y_vals in curves.items():
        is_time = (label == time_match)
        is_space = (label == space_match)

        line_width = 4 if (is_time or is_space) else 1.5
        opacity = 1.0 if (is_time or is_space) else 0.3
        dash = None

        name = label
        if is_time and is_space:
            name = f"{label}  ← Your Time & Space"
        elif is_time:
            name = f"{label}  ← Your Time"
        elif is_space:
            name = f"{label}  ← Your Space"

        fig.add_trace(go.Scatter(
            x=n_vals, y=y_vals, mode="lines", name=name,
            line=dict(color=colors.get(label, "#636E72"), width=line_width, dash=dash),
            opacity=opacity,
            hovertemplate=f"{label}<br>n=%{{x}}<br>ops=%{{y:.0f}}<extra></extra>",
        ))

    fig.update_layout(
        title=dict(text="Complexity Growth Curves", font=dict(size=16, family="Inter", color="#2D3436")),
        xaxis=dict(title="Input Size (n)", gridcolor="#F0F0F0", zerolinecolor="#F0F0F0"),
        yaxis=dict(title="Operations", gridcolor="#F0F0F0", zerolinecolor="#F0F0F0", type="log"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter", color="#2D3436"),
        legend=dict(
            font=dict(size=11),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#EDF2F7",
            borderwidth=1,
        ),
        height=420,
        margin=dict(l=60, r=20, t=50, b=50),
        hovermode="x unified",
    )

    return fig
