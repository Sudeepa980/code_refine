"""
Code comparison: diff and AI summary of differences (Groq).
"""
from typing import Optional, Tuple
from .groq_client import chat


def compare_and_summarize(code_a: str, code_b: str, label_a: str = "Code A", label_b: str = "Code B") -> Tuple[Optional[str], Optional[str]]:
    """Returns (summary_text, None) or (None, error_message)."""
    system = (
        "You are a code reviewer. Compare the two code snippets and list key differences: "
        "logic, structure, complexity, style. Use 5-8 short bullet points. No code output."
    )
    user = f"{label_a}:\n```\n{code_a[:2000]}\n```\n\n{label_b}:\n```\n{code_b[:2000]}\n```"
    return chat(system, user, max_tokens=500)
