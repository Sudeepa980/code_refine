"""
AI code optimization: takes code, returns optimized version + explanation.
"""
from typing import Optional, Tuple
from .groq_client import chat


def optimize_code(code: str, language: str, time_complexity: str, issues_summary: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns (optimized_code_block, None) or (None, error_message).
    The response includes the optimized code and a brief explanation.
    """
    system = (
        "You are an expert code optimizer. Given the code, its current time complexity, and known issues, "
        "return an OPTIMIZED version. Format your response EXACTLY as:\n\n"
        "OPTIMIZED CODE:\n```\n<the optimized code>\n```\n\n"
        "CHANGES MADE:\n- <bullet 1>\n- <bullet 2>\n...\n\n"
        "NEW COMPLEXITY: <new time complexity>\n\n"
        "Keep explanations concise. Fix all bugs. Improve efficiency. Use best practices for the language."
    )
    user = (
        f"Language: {language.upper()}\n"
        f"Current complexity: {time_complexity}\n"
        f"Known issues: {issues_summary or 'None'}\n\n"
        f"Code:\n```\n{code[:5000]}\n```"
    )
    return chat(system, user, max_tokens=2500)


def suggest_alternative_approach(code: str, language: str) -> Tuple[Optional[str], Optional[str]]:
    """Suggest a completely different algorithmic approach if possible."""
    system = (
        "You are an algorithm expert. Analyze the code and suggest if there is a fundamentally "
        "better algorithm or data structure that could be used. If the current approach is already "
        "optimal, say so. Be concise — max 5 bullet points."
    )
    user = f"Language: {language.upper()}\n\nCode:\n```\n{code[:4000]}\n```"
    return chat(system, user, max_tokens=600)
