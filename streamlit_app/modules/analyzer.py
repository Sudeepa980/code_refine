"""
Static analysis + total time and space complexity for Python and C.
Estimates overall code complexity (not just loop complexity).
"""
import ast
import re
from typing import List, Dict, Any, Tuple


def detect_language(source: str) -> str:
    """Auto-detect whether code is C or Python. Returns 'c' or 'python'."""
    lines = source.strip().splitlines()
    c_score = 0
    py_score = 0

    for line in lines:
        stripped = line.strip()
        # Strong C indicators
        if re.match(r'^#include\s*[<"]', stripped):
            c_score += 10
        if re.match(r'^(int|void|char|float|double|long|unsigned|signed|short)\s+\w+\s*\(', stripped):
            c_score += 5
        if 'printf(' in stripped or 'scanf(' in stripped or 'malloc(' in stripped or 'free(' in stripped:
            c_score += 3
        if re.search(r'->', stripped):
            c_score += 2
        if stripped.endswith(';') and not stripped.startswith('#'):
            c_score += 1
        if re.match(r'^(struct|typedef|enum)\s', stripped):
            c_score += 4
        if 'int main(' in stripped or 'void main(' in stripped:
            c_score += 8

        # Strong Python indicators
        if re.match(r'^(def|class)\s+\w+', stripped):
            py_score += 5
        if re.match(r'^import\s+\w+|^from\s+\w+\s+import', stripped):
            py_score += 8
        if 'print(' in stripped and 'printf(' not in stripped:
            py_score += 3
        if stripped.startswith('elif ') or stripped.startswith('except ') or stripped.startswith('finally:'):
            py_score += 5
        if 'self.' in stripped:
            py_score += 4
        if stripped.endswith(':') and re.match(r'^(if|for|while|def|class|elif|else|try|except|with)\b', stripped):
            py_score += 2
        if re.search(r'\b(True|False|None)\b', stripped):
            py_score += 1
        if 'range(' in stripped or 'len(' in stripped or 'input(' in stripped:
            py_score += 2

    return "python" if py_score > c_score else "c"


def analyze_static(language: str, source: str) -> List[Dict[str, Any]]:
    """Static issues: syntax, unused vars, bad practices."""
    lang = language.lower()
    issues = []
    if lang == "python":
        return _static_python(source, issues)
    return _static_c(source, issues)


def _line(lines: List[str], lineno: int) -> str:
    if 1 <= lineno <= len(lines):
        return lines[lineno - 1].strip()
    return ""


def _static_python(source: str, issues: List) -> List:
    lines = source.splitlines()
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        issues.append({"line": e.lineno or 1, "type": "syntax_error", "message": str(e.msg), "category": "static"})
        return issues
    assigned, used = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            ctx = getattr(node, "ctx", None)
            if type(ctx) == ast.Store:
                assigned.add(node.id)
            elif type(ctx) == ast.Load:
                used.add(node.id)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for a in node.args.args:
                assigned.add(a.arg)
    unused = assigned - used - {"_"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and type(getattr(node, "ctx", None)) == ast.Store and node.id in unused:
            issues.append({"line": node.lineno, "type": "unused_variable", "message": f"Unused: {node.id}", "category": "static", "snippet": _line(lines, node.lineno)})
    for i, line in enumerate(lines, 1):
        if len(line) > 100:
            issues.append({"line": i, "type": "formatting", "message": "Line > 100 chars", "category": "static"})
    return issues


def _static_c(source: str, issues: List) -> List:
    lines = source.splitlines()
    brace_depth = 0
    paren_depth = 0
    in_block_comment = False

    for i, raw_line in enumerate(lines, 1):
        line = raw_line.strip()

        # Track block comments
        if in_block_comment:
            if "*/" in line:
                in_block_comment = False
                line = line[line.index("*/") + 2:].strip()
                if not line:
                    continue
            else:
                continue
        if "/*" in line:
            before = line[:line.index("/*")].strip()
            after = line[line.index("/*"):]
            if "*/" not in after:
                in_block_comment = True
                line = before
                if not line:
                    continue
            else:
                line = before + after[after.index("*/") + 2:]
                line = line.strip()

        # Skip blank lines and single-line comments
        if not line or line.startswith("//"):
            continue

        # Strip trailing inline comment
        code_part = re.sub(r'//.*$', '', line).strip()
        if not code_part:
            continue

        # Line length
        if len(raw_line) > 100:
            issues.append({"line": i, "type": "formatting", "message": "Line > 100 chars", "category": "static"})

        # Track braces and parens
        brace_depth += code_part.count("{") - code_part.count("}")
        paren_depth += code_part.count("(") - code_part.count(")")

        # --- Missing semicolon detection ---
        _check_c_semicolon(code_part, i, raw_line, issues)

        # --- Assignment in condition (= vs ==) ---
        cond_match = re.search(r'\b(if|while)\s*\((.+)\)', code_part)
        if cond_match:
            cond_body = cond_match.group(2)
            if re.search(r'(?<![=!<>])=(?!=)', cond_body):
                issues.append({"line": i, "type": "warning", "message": f"Possible assignment in condition (use == for comparison?)", "category": "static", "snippet": raw_line.strip()})

    # Unbalanced braces
    if brace_depth != 0:
        issues.append({"line": len(lines), "type": "syntax_error", "message": f"Unbalanced braces (depth {brace_depth} at end of file)", "category": "static"})
    if paren_depth != 0:
        issues.append({"line": len(lines), "type": "syntax_error", "message": f"Unbalanced parentheses (depth {paren_depth} at end of file)", "category": "static"})

    return issues


def _check_c_semicolon(code: str, lineno: int, raw_line: str, issues: List):
    """Check if a C statement line is missing its trailing semicolon."""
    # Lines that never need a semicolon at the end
    if not code:
        return

    # Preprocessor directives
    if code.startswith("#"):
        return

    # Lines ending with { or } or : (labels, case) or \ (continuation)
    if code.endswith(("{", "}", "\\", ":")):
        return

    # Already has semicolon
    if code.endswith(";"):
        return

    # Lines ending with comma (multi-line args, array init)
    if code.endswith(","):
        return

    # Lines ending with ) that are control-flow headers (if, for, while, switch, else if)
    if code.endswith(")"):
        if re.match(r'^(if|else\s+if|for|while|switch)\s*\(', code):
            return
        # Function definition: requires a return type before the name, e.g. "int main()" or "void foo(int a)"
        # Must have at least two words before the parenthesis (type + name)
        if re.match(r'^([\w\*]+\s+)+\w+\s*\(.*\)\s*$', code):
            return

    # Bare else
    if re.match(r'^(else)\s*$', code):
        return

    # struct/enum/union opening
    if re.match(r'^(typedef\s+)?(struct|enum|union)\b', code) and "{" not in code and ";" not in code:
        return

    # If we get here, the line likely needs a semicolon
    # Only flag lines that look like actual statements
    is_statement = (
        re.match(r'^(return|break|continue|goto)\b', code)
        or re.match(r'^[\w][\w\s\*]*\w+\s*[=\[\(]', code)  # declaration/assignment/call
        or re.match(r'^\w+\s*\(', code)                       # function call
        or re.match(r'^[\w\.\-\>\[\]]+\s*[\+\-\*\/\%]?=', code)  # assignment
        or re.match(r'^\+\+|^\-\-', code)                     # increment/decrement
        or re.match(r'^.*\)\s*$', code)                        # ends with ) but not control flow
    )
    if is_statement:
        issues.append({
            "line": lineno,
            "type": "syntax_error",
            "message": "Missing semicolon at end of statement",
            "category": "static",
            "snippet": raw_line.strip(),
        })


def analyze_complexity(language: str, source: str) -> Tuple[str, str, List[Dict], List[Dict]]:
    """
    Returns (time_complexity, space_complexity, time_reasons, space_reasons).
    Estimates total code time/space complexity with reasoning.
    """
    lang = language.lower()
    if lang == "python":
        return _complexity_python(source)
    return _complexity_c(source)


def _complexity_python(source: str) -> Tuple[str, str, List[Dict], List[Dict]]:
    time_reasons = []
    space_reasons = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return "O(1)", "O(1)", [], []

    lines = source.splitlines()
    loop_depth = 0
    max_loop_depth = 0
    has_recursion = False
    has_sort = False
    has_nested_data = False
    recursion_funcs = set()

    def depth_of(node: ast.AST, d: int) -> int:
        if isinstance(node, (ast.For, ast.While)):
            inner = d + 1
            for c in ast.iter_child_nodes(node):
                inner = max(inner, depth_of(c, d + 1))
            return inner
        out = d
        for c in ast.iter_child_nodes(node):
            out = max(out, depth_of(c, d))
        return out

    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.While)):
            depth = depth_of(node, 1)
            max_loop_depth = max(max_loop_depth, depth)
            if depth == 1:
                time_reasons.append({"line": node.lineno, "reason": "Single loop", "contribution": "O(n)", "snippet": _line(lines, node.lineno)})
            elif depth == 2:
                time_reasons.append({"line": node.lineno, "reason": "Nested loop", "contribution": "O(n²)", "snippet": _line(lines, node.lineno)})
            else:
                time_reasons.append({"line": node.lineno, "reason": "Deep nesting", "contribution": "O(n³)+", "snippet": _line(lines, node.lineno)})
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name):
                if f.id == "sorted":
                    has_sort = True
                    time_reasons.append({"line": node.lineno, "reason": "sorted()", "contribution": "O(n log n)", "snippet": _line(lines, node.lineno)})
                if f.id and _calls_self(tree, f.id):
                    has_recursion = True
                    recursion_funcs.add(f.id)
                    time_reasons.append({"line": node.lineno, "reason": "Recursion", "contribution": "Depends on depth", "snippet": _line(lines, node.lineno)})
        if isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp)):
            has_nested_data = True
            space_reasons.append({"line": node.lineno, "reason": "Comprehension", "contribution": "O(n)", "snippet": _line(lines, node.lineno)})

    # Overall time complexity
    if max_loop_depth >= 3 or has_recursion:
        time_complexity = "O(n³) or higher"
    elif max_loop_depth == 2:
        time_complexity = "O(n²)"
    elif has_sort and max_loop_depth <= 1:
        time_complexity = "O(n log n)"
    elif max_loop_depth == 1:
        time_complexity = "O(n)"
    else:
        time_complexity = "O(1)"

    # Space: extra structures
    if has_nested_data or max_loop_depth >= 1:
        space_complexity = "O(n)" if max_loop_depth <= 1 else "O(n²)"
    else:
        space_complexity = "O(1)"

    if not space_reasons:
        space_reasons.append({"line": None, "reason": "No large auxiliary structures", "contribution": space_complexity, "snippet": ""})

    return time_complexity, space_complexity, time_reasons, space_reasons


def _calls_self(tree: ast.AST, name: str) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            for n in ast.walk(node):
                if isinstance(n, ast.Call) and isinstance(getattr(n.func, "id", None), str) and n.func.id == name:
                    return True
    return False


def _complexity_c(source: str) -> Tuple[str, str, List[Dict], List[Dict]]:
    lines = source.splitlines()
    depth = 0
    max_depth = 0
    time_reasons = []
    for i, line in enumerate(lines, 1):
        if re.match(r"\s*(for|while)\s*\(", line):
            depth += 1
            max_depth = max(max_depth, depth)
            if depth == 1:
                time_reasons.append({"line": i, "reason": "Single loop", "contribution": "O(n)", "snippet": line.strip()})
            elif depth == 2:
                time_reasons.append({"line": i, "reason": "Nested loop", "contribution": "O(n²)", "snippet": line.strip()})
            else:
                time_reasons.append({"line": i, "reason": "Deep nesting", "contribution": "O(n³)+", "snippet": line.strip()})
        if re.match(r"\s*}", line):
            depth = max(0, depth - 1)
    if max_depth >= 3:
        tc, sc = "O(n³)+", "O(n²)"
    elif max_depth == 2:
        tc, sc = "O(n²)", "O(n)"
    elif max_depth == 1:
        tc, sc = "O(n)", "O(n)"
    else:
        tc, sc = "O(1)", "O(1)"
    space_reasons = [{"line": None, "reason": "Loop variables / buffers", "contribution": sc, "snippet": ""}]
    return tc, sc, time_reasons, space_reasons
