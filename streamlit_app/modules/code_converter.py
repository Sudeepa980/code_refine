"""
Code conversion between C and Python using Groq.
"""
from typing import Optional, Tuple
from .groq_client import chat


def convert_code(code: str, from_lang: str, to_lang: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Convert code from one language to the other. Returns (converted_code, None) or (None, error_message).
    """
    system = (
        "You are an expert at translating code between C and Python. "
        "Output only the converted code, no explanations. Preserve logic and structure. Use standard idioms for the target language."
    )
    user = f"Convert this {from_lang.upper()} code to {to_lang.upper()}:\n\n```\n{code[:6000]}\n```"
    return chat(system, user, max_tokens=2000)
