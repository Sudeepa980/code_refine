"""
Groq API client (free, no billing required).
Get your key at https://console.groq.com — sign up with email/Google.
Set GROQ_API_KEY in .env (in streamlit_app folder) or as an environment variable.
"""
import os
from pathlib import Path
from typing import Optional, Tuple

_client = None
DEFAULT_MODEL = "llama-3.1-8b-instant"


def _load_env():
    base = Path(__file__).resolve().parent.parent
    for path in [base / ".env", Path.cwd() / ".env", Path.cwd() / "streamlit_app" / ".env"]:
        if path.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(path)
                break
            except ImportError:
                pass


def _get_model() -> str:
    return (os.environ.get("GROQ_MODEL") or DEFAULT_MODEL).strip()


def _get_client():
    global _client
    if _client is False:
        return None, "Groq API key missing or invalid."
    if _client is not None:
        return _client, None
    try:
        _load_env()
        key = (os.environ.get("GROQ_API_KEY") or "").strip()
        if not key:
            return None, "GROQ_API_KEY not set. Get a free key at https://console.groq.com and add it to streamlit_app/.env"
        from groq import Groq
        _client = Groq(api_key=key)
        return _client, None
    except Exception as e:
        _client = False
        return None, str(e)


def chat(system: str, user: str, max_tokens: int = 800) -> Tuple[Optional[str], Optional[str]]:
    """
    Send system + user message to Groq.
    Returns (response_text, None) on success, or (None, error_message) on failure.
    """
    client, err = _get_client()
    if err:
        return None, err
    try:
        model = _get_model()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=0.3,
        )
        text = response.choices[0].message.content.strip()
        if text:
            return text, None
        return None, "Empty response from Groq"
    except Exception as e:
        return None, str(e)


def check_key_status() -> Tuple[bool, str]:
    """
    Check if Groq API key is set and client can be created.
    Returns (ok, message).
    """
    client, err = _get_client()
    if err:
        return False, err
    return True, f"Groq API ready (model: {_get_model()})"
