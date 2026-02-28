"""
History CRUD: save, list, update, rename, delete user records.
Types: complexity, optimized, explanation, bugfix, quality, review, conversion, comparison
"""
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional

_here = Path(__file__).resolve().parent.parent
DB_PATH = _here / "database" / "coderefine.db"


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            title TEXT DEFAULT '',
            language_from TEXT,
            language_to TEXT,
            code_input TEXT,
            code_output TEXT,
            report_json TEXT,
            score INTEGER,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_history_user ON history(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_history_created ON history(created_at DESC)")
    _migrate_title_column(conn)
    conn.commit()


def _migrate_title_column(conn):
    """Add title column if missing (upgrade from older schema)."""
    cur = conn.cursor()
    try:
        cur.execute("SELECT title FROM history LIMIT 1")
    except sqlite3.OperationalError:
        cur.execute("ALTER TABLE history ADD COLUMN title TEXT DEFAULT ''")
        conn.commit()


def save_history(
    user_id: int,
    type_: str,
    title: str = "",
    language_from: Optional[str] = None,
    language_to: Optional[str] = None,
    code_input: str = "",
    code_output: str = "",
    report_json: Optional[dict] = None,
    score: Optional[int] = None,
) -> int:
    conn = get_conn()
    ensure_schema(conn)
    if not title:
        title = _auto_title(type_, code_input, language_from)
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO history (user_id, type, title, language_from, language_to, code_input, code_output, report_json, score)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, type_, title, language_from, language_to, code_input[:50000], code_output[:50000],
         json.dumps(report_json) if report_json else None, score),
    )
    conn.commit()
    hid = cur.lastrowid
    conn.close()
    return hid


def _auto_title(type_: str, code: str, lang: Optional[str]) -> str:
    first_line = (code or "").strip().splitlines()[0][:60] if code else ""
    labels = {
        "complexity": "Complexity Analysis",
        "optimized": "Optimized Solution",
        "explanation": "AI Explanation",
        "bugfix": "Bug Fix Suggestions",
        "quality": "Quality Score",
        "review": "Full Code Review",
        "conversion": "Code Conversion",
        "comparison": "Code Comparison",
    }
    prefix = labels.get(type_, type_.title())
    lang_tag = f" ({lang.upper()})" if lang else ""
    snippet = f" — {first_line}" if first_line else ""
    return f"{prefix}{lang_tag}{snippet}"


def get_history(user_id: int, limit: int = 100, type_filter: Optional[str] = None) -> List[Dict]:
    conn = get_conn()
    ensure_schema(conn)
    cur = conn.cursor()
    if type_filter:
        cur.execute(
            "SELECT id, type, title, language_from, language_to, code_input, code_output, report_json, score, created_at FROM history WHERE user_id = ? AND type = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, type_filter, limit),
        )
    else:
        cur.execute(
            "SELECT id, type, title, language_from, language_to, code_input, code_output, report_json, score, created_at FROM history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        )
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        if d.get("report_json"):
            try:
                d["report_json"] = json.loads(d["report_json"])
            except Exception:
                d["report_json"] = None
        out.append(d)
    return out


def get_one(user_id: int, history_id: int) -> Optional[Dict]:
    conn = get_conn()
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, type, title, language_from, language_to, code_input, code_output, report_json, score, created_at FROM history WHERE user_id = ? AND id = ?",
        (user_id, history_id),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    if d.get("report_json"):
        try:
            d["report_json"] = json.loads(d["report_json"])
        except Exception:
            d["report_json"] = None
    return d


def rename_history(user_id: int, history_id: int, new_title: str) -> bool:
    conn = get_conn()
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(
        "UPDATE history SET title = ? WHERE id = ? AND user_id = ?",
        (new_title.strip(), history_id, user_id),
    )
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok


def update_history_report(user_id: int, history_id: int, report_json: dict, score: Optional[int] = None) -> bool:
    conn = get_conn()
    ensure_schema(conn)
    cur = conn.cursor()
    if score is not None:
        cur.execute(
            "UPDATE history SET report_json = ?, score = ? WHERE id = ? AND user_id = ?",
            (json.dumps(report_json), score, history_id, user_id),
        )
    else:
        cur.execute(
            "UPDATE history SET report_json = ? WHERE id = ? AND user_id = ?",
            (json.dumps(report_json), history_id, user_id),
        )
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok


def delete_history(user_id: int, history_id: int) -> bool:
    conn = get_conn()
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("DELETE FROM history WHERE id = ? AND user_id = ?", (history_id, user_id))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok


def get_type_counts(user_id: int) -> Dict[str, int]:
    conn = get_conn()
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT type, COUNT(*) as cnt FROM history WHERE user_id = ? GROUP BY type", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return {r["type"]: r["cnt"] for r in rows}
