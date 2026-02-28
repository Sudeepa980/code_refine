"""
AI line-by-line code explanation using Groq.
"""
from typing import List, Dict, Optional, Tuple
from .groq_client import chat


def explain_line_by_line(code: str, language: str) -> Tuple[Optional[str], Optional[str]]:
    """Returns (explanation_text, None) or (None, error_message)."""
    system = "You are a coding mentor. Explain the given code line-by-line briefly. Use numbered lines. Keep each line explanation to one short sentence. Output plain text only."
    user = f"Language: {language}\n\nCode:\n```\n{code[:4000]}\n```"
    return chat(system, user, max_tokens=1500)


def explain_lines_batch(code: str, language: str, line_numbers: List[int]) -> Tuple[Optional[str], Optional[str]]:
    """Explain only the given line numbers. Returns (text, None) or (None, error)."""
    lines = code.splitlines()
    snippet = "\n".join(f"{i}: {lines[i-1]}" for i in line_numbers if 1 <= i <= len(lines))
    if not snippet:
        return None, None
    system = "Explain these lines of code in 1-2 short sentences each. Be concise."
    user = f"Language: {language}\n\nLines:\n{snippet}"
    return chat(system, user, max_tokens=500)
