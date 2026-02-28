"""
History — ChatGPT-style interface with filter, rename, edit, delete.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from auth.auth import is_authenticated
from modules.ui_components import inject_global_css
from utils.db import get_history, get_one, rename_history, delete_history, get_type_counts

if not is_authenticated():
    st.warning("Please sign in from the main page.")
    st.stop()

st.set_page_config(page_title="History | CodeRefine", page_icon="📜", layout="wide")
inject_global_css()

user_id = st.session_state["user_id"]

TYPE_META = {
    "complexity":  {"icon": "⏱", "color": "#6C5CE7", "label": "Complexity"},
    "quality":     {"icon": "💯", "color": "#00B894", "label": "Quality"},
    "optimized":   {"icon": "⚡", "color": "#E17055", "label": "Optimized"},
    "explanation":  {"icon": "🧠", "color": "#0984E3", "label": "Explanation"},
    "bugfix":      {"icon": "🐛", "color": "#D63031", "label": "Bug Fix"},
    "alternative": {"icon": "🔀", "color": "#00CEC9", "label": "Alternative"},
    "review":      {"icon": "🔍", "color": "#6C5CE7", "label": "Full Review"},
    "conversion":  {"icon": "🔄", "color": "#E17055", "label": "Conversion"},
    "comparison":  {"icon": "⚖️", "color": "#FDCB6E", "label": "Comparison"},
}


def type_pill(type_: str) -> str:
    m = TYPE_META.get(type_, {"icon": "📄", "color": "#636E72", "label": type_})
    return f'<span class="type-pill" style="background:{m["color"]}20; color:{m["color"]};">{m["icon"]} {m["label"]}</span>'


# ═══════════════════════════════════
#    SIDEBAR: Conversation List
# ═══════════════════════════════════
with st.sidebar:
    st.markdown("""
<div style="padding:12px 0 4px;">
    <div style="font-size:1rem; font-weight:700; color:#A29BFE;">📜 History</div>
</div>
""", unsafe_allow_html=True)

    # Filter
    type_counts = get_type_counts(user_id)
    all_types = ["All"] + sorted(type_counts.keys())
    filter_type = st.selectbox("Filter by type", all_types, key="hist_type_filter", label_visibility="collapsed")
    filter_val = None if filter_type == "All" else filter_type

    rows = get_history(user_id, limit=100, type_filter=filter_val)

    if not rows:
        st.caption("No history yet.")
    else:
        st.caption(f"{len(rows)} entries")
        for r in rows:
            m = TYPE_META.get(r["type"], {"icon": "📄", "color": "#636E72", "label": r["type"]})
            title = r.get("title") or f'{m["label"]} — {(r.get("created_at") or "")[:10]}'
            title_short = title[:45] + "..." if len(title) > 45 else title
            ts = (r.get("created_at") or "")[:16]
            if st.button(f'{m["icon"]} {title_short}', key=f"nav_{r['id']}", use_container_width=True):
                st.session_state["hist_selected"] = r["id"]


# ═══════════════════════════════════
#    MAIN: Chat-like view
# ═══════════════════════════════════
st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
    <span style="font-size:2rem;">📜</span>
    <div>
        <div style="font-size:1.6rem; font-weight:800; color:#2D3436;">History</div>
        <div style="font-size:0.85rem; color:#636E72;">Browse, edit, rename, or delete past analyses</div>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# Type filter pills at top
counts = get_type_counts(user_id)
if counts:
    pills_html = ""
    for t, cnt in sorted(counts.items()):
        m = TYPE_META.get(t, {"icon": "📄", "color": "#636E72", "label": t})
        pills_html += f'<span style="display:inline-block; margin:4px; padding:4px 14px; border-radius:20px; background:{m["color"]}15; color:{m["color"]}; font-size:0.78rem; font-weight:600;">{m["icon"]} {m["label"]} <strong>{cnt}</strong></span>'
    st.markdown(f'<div style="margin-bottom:16px;">{pills_html}</div>', unsafe_allow_html=True)

# Get selected entry or show list
selected_id = st.session_state.get("hist_selected")

if selected_id:
    entry = get_one(user_id, selected_id)
    if not entry:
        st.warning("Entry not found.")
        st.session_state.pop("hist_selected", None)
        st.stop()

    m = TYPE_META.get(entry["type"], {"icon": "📄", "color": "#636E72", "label": entry["type"]})
    title = entry.get("title") or f'{m["label"]}'
    ts = (entry.get("created_at") or "")[:19]

    # Back button
    if st.button("← Back to all entries", key="back_btn"):
        st.session_state.pop("hist_selected", None)
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Chat bubble: User input ──
    st.markdown(f"""
<div class="chat-msg">
    <div class="avatar" style="background:#6C5CE7;">👤</div>
    <div class="bubble">
        <div class="bubble-header">
            <span class="bubble-title">Your Code</span>
            <span class="bubble-time">{ts} &middot; {type_pill(entry["type"])}</span>
        </div>
        <div class="bubble-body">
            <pre style="background:#1E1E2E; color:#CDD6F4; padding:12px; border-radius:8px; font-size:12px; overflow-x:auto; font-family:'JetBrains Mono',monospace;">{__import__('html').escape((entry.get('code_input') or '')[:2000])}</pre>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ── Chat bubble: AI response ──
    report = entry.get("report_json") or {}
    response_parts = []

    if entry.get("code_output"):
        response_parts.append(f"**Converted Code:**\n```\n{entry['code_output'][:2000]}\n```")

    if report.get("time_complexity"):
        response_parts.append(f"**Time Complexity:** {report['time_complexity']}\n**Space Complexity:** {report.get('space_complexity', '—')}")
    if report.get("time_reasons"):
        for r in report["time_reasons"][:5]:
            response_parts.append(f"- Line {r.get('line', '?')}: {r.get('reason', '')} → **{r.get('contribution', '')}**")
    if report.get("score") is not None:
        response_parts.append(f"**Quality Score:** {report['score']}/100")
    if report.get("reasons"):
        for r in report["reasons"]:
            response_parts.append(f"- {r}")
    if report.get("explanation"):
        response_parts.append(f"**AI Explanation:**\n{report['explanation'][:1500]}")
    if report.get("bugs"):
        response_parts.append(f"**Bug Detection:**\n{report['bugs'][:1500]}")
    if report.get("alternative"):
        response_parts.append(f"**Alternative Approach:**\n{report['alternative'][:1500]}")
    if report.get("ai_explanation"):
        response_parts.append(f"**AI Explanation:**\n{report['ai_explanation'][:1500]}")
    if report.get("ai_bugs"):
        response_parts.append(f"**Bug Fixes:**\n{report['ai_bugs'][:1500]}")
    if report.get("summary"):
        response_parts.append(f"**Comparison Summary:**\n{report['summary'][:1500]}")

    if entry.get("score") is not None and not report.get("score"):
        response_parts.append(f"**Score:** {entry['score']}/100")

    ai_response = "\n\n".join(response_parts) if response_parts else "No detailed report saved."

    st.markdown(f"""
<div class="chat-msg">
    <div class="avatar" style="background:#00B894;">⚡</div>
    <div class="bubble" style="border-radius:16px 0 16px 16px;">
        <div class="bubble-header">
            <span class="bubble-title">CodeRefine AI</span>
            <span class="bubble-time">{m["icon"]} {m["label"]}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
    st.markdown(ai_response)

    # ── Actions: Rename / Delete ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    act_col1, act_col2, act_col3 = st.columns([2, 1, 1])

    with act_col1:
        new_title = st.text_input("Rename this entry", value=title, key=f"rename_{entry['id']}")
        if new_title != title:
            if st.button("💾 Save Name", key=f"save_name_{entry['id']}"):
                rename_history(user_id, entry["id"], new_title)
                st.success("Renamed!")
                st.rerun()

    with act_col3:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Delete", key=f"del_{entry['id']}", type="secondary"):
            st.session_state[f"confirm_del_{entry['id']}"] = True

        if st.session_state.get(f"confirm_del_{entry['id']}"):
            st.warning("Are you sure?")
            dc1, dc2 = st.columns(2)
            with dc1:
                if st.button("Yes, delete", key=f"yes_del_{entry['id']}", type="primary"):
                    delete_history(user_id, entry["id"])
                    st.session_state.pop("hist_selected", None)
                    st.session_state.pop(f"confirm_del_{entry['id']}", None)
                    st.success("Deleted!")
                    st.rerun()
            with dc2:
                if st.button("Cancel", key=f"no_del_{entry['id']}"):
                    st.session_state.pop(f"confirm_del_{entry['id']}", None)
                    st.rerun()

else:
    # ═══════════════════════════════════
    #    FULL LIST VIEW (no selection)
    # ═══════════════════════════════════
    rows_main = get_history(user_id, limit=100, type_filter=filter_val if filter_type != "All" else None)

    if not rows_main:
        st.markdown("""
<div style="text-align:center; padding:60px 20px; color:#636E72;">
    <div style="font-size:3rem; margin-bottom:12px;">📭</div>
    <div style="font-size:1.1rem; font-weight:600;">No history yet</div>
    <div style="font-size:0.85rem; margin-top:4px;">Run a Code Review feature to see results here.</div>
</div>
""", unsafe_allow_html=True)
        st.stop()

    # Render as chat messages
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    for r in rows_main:
        m = TYPE_META.get(r["type"], {"icon": "📄", "color": "#636E72", "label": r["type"]})
        title = r.get("title") or f'{m["label"]}'
        title_short = title[:70] + "..." if len(title) > 70 else title
        ts = (r.get("created_at") or "")[:16]
        score_badge = f' &middot; Score: <strong>{r["score"]}</strong>' if r.get("score") is not None else ""
        code_preview = __import__('html').escape((r.get("code_input") or "")[:120]).replace("\n", " ")

        st.markdown(f"""
<div class="chat-msg">
    <div class="avatar" style="background:{m['color']};">{m['icon']}</div>
    <div class="bubble">
        <div class="bubble-header">
            <span class="bubble-title">{__import__('html').escape(title_short)}</span>
            <span class="bubble-time">{ts}{score_badge}</span>
        </div>
        <div class="bubble-body">
            <div>{type_pill(r['type'])}</div>
            <div style="margin-top:8px; color:#636E72; font-size:0.8rem; font-family:'JetBrains Mono',monospace;">{code_preview}{'...' if len(r.get('code_input','')) > 120 else ''}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

        # Expand button
        if st.button(f"Open →  {title_short[:30]}", key=f"open_{r['id']}", use_container_width=True):
            st.session_state["hist_selected"] = r["id"]
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
