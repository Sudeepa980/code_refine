"""
Auth database helpers: user CRUD, password hashing.
"""
import sqlite3
import hashlib
import secrets
from pathlib import Path

_here = Path(__file__).resolve().parent.parent
DB_PATH = _here / "database" / "coderefine.db"


def _ensure_schema(conn: sqlite3.Connection) -> None:
    """Create users and history tables if they don't exist."""
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
    conn.commit()


def _hash(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000).hex()


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    _ensure_schema(conn)
    return conn


def create_user(email: str, password: str, name: str = "") -> tuple:
    """Returns (user_id, None) or (None, error_message)."""
    email = email.strip().lower()
    salt = secrets.token_hex(16)
    stored = f"{salt}:{_hash(password, salt)}"
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
            (email, stored, name or email),
        )
        conn.commit()
        return (cur.lastrowid, None)
    except sqlite3.IntegrityError:
        return (None, "Email already registered.")
    finally:
        conn.close()


def get_user_by_email(email: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, email, password_hash, name FROM users WHERE email = ?", (email.strip().lower(),))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, email, name FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def check_password(email: str, password: str) -> dict | None:
    """Returns user dict (id, email, name) if valid, else None."""
    user = get_user_by_email(email)
    if not user:
        return None
    stored = user["password_hash"]
    if ":" not in stored:
        return None
    salt, hash_part = stored.split(":", 1)
    if _hash(password, salt) == hash_part:
        return {"id": user["id"], "email": user["email"], "name": user["name"]}
    return None
