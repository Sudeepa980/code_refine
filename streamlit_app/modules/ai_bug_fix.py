"""
AI bug detection and auto-fix suggestions using Groq.
"""
from typing import List, Dict, Optional, Tuple
from .groq_client import chat


def detect_bugs_and_suggest_fixes(code: str, language: str, static_issues: List[Dict]) -> Tuple[Optional[str], Optional[str]]:
    """Returns (analysis_text, None) or (None, error_message)."""
    issues_text = "\n".join([f"Line {i.get('line')}: {i.get('message', '')}" for i in static_issues[:15]])
    system = (
        "You are a senior developer. For the given code and any listed static issues, "
        "list potential bugs and give 1-2 line fix suggestions. Use bullet points. Maximum 8 bullets. No long paragraphs."
    )
    user = f"Language: {language}\n\nCode:\n```\n{code[:3500]}\n```\n\nReported issues:\n{issues_text or 'None'}"
    return chat(system, user, max_tokens=600)


def get_fix_suggestion_for_line(code: str, language: str, line_number: int, issue: str) -> Tuple[Optional[str], Optional[str]]:
    """Single line fix suggestion. Returns (text, None) or (None, error)."""
    lines = code.splitlines()
    snippet = lines[line_number - 1] if 1 <= line_number <= len(lines) else ""
    system = "Suggest a single-line fix. Reply with only the corrected line or a one-sentence instruction."
    user = f"Language: {language}. Line {line_number}: {issue}\nCode line: {snippet}"
    return chat(system, user, max_tokens=150)
