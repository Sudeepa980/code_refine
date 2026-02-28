"""
App configuration: paths, env vars, constants.
"""
import os
from pathlib import Path

# Load .env if present
_env = Path(__file__).resolve().parent / ".env"
if _env.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env)
    except ImportError:
        pass

# Paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATABASE_DIR / "coderefine.db"

# Groq (free, no billing – get key at https://console.groq.com)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")

# Session
SESSION_COOKIE_NAME = "coderefine_session"
