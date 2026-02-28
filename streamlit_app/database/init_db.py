"""
Initialize SQLite schema: users, sessions, history.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "coderefine.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn):
    cur = conn.cursor()
    # Users
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    # History: code reviews, conversions, comparisons
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


if __name__ == "__main__":
    conn = get_conn()
    init_schema(conn)
    conn.close()
    print("Database initialized.")
