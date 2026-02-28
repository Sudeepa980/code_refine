"""
Code quality score 0-100 based on static issues, complexity, and structure.
"""
from typing import List, Dict, Any, Tuple


def compute_quality_score(
    static_issues: List[Dict],
    time_complexity: str,
    space_complexity: str,
    has_syntax_error: bool = False,
) -> Tuple[int, List[str]]:
    """
    Returns (score 0-100, list of short feedback reasons).
    """
    score = 100
    reasons = []

    if has_syntax_error:
        score -= 40
        reasons.append("Syntax error (-40)")
    else:
        # Deduct by static issue count
        critical = sum(1 for i in static_issues if i.get("type") == "syntax_error")
        major = sum(1 for i in static_issues if i.get("type") in ("unused_variable", "bad_practice"))
        minor = sum(1 for i in static_issues if i.get("type") in ("formatting",))
        score -= critical * 15
        score -= major * 5
        score -= minor * 2
        if critical:
            reasons.append(f"{critical} critical issue(s)")
        if major:
            reasons.append(f"{major} major issue(s)")
        if minor:
            reasons.append(f"{minor} minor issue(s)")

    # Complexity penalty (worse complexity = small penalty for "quality")
    if "O(n³)" in time_complexity or "higher" in time_complexity:
        score -= 5
        reasons.append("High time complexity")
    elif "O(n²)" in time_complexity:
        score -= 2
        reasons.append("Quadratic time complexity")

    score = max(0, min(100, score))
    if score >= 90:
        reasons.insert(0, "Good structure and style")
    elif score >= 70:
        reasons.insert(0, "Acceptable with some improvements")
    else:
        reasons.insert(0, "Needs improvement")

    return score, reasons
