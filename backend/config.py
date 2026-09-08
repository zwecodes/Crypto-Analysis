import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_DIR.parent

load_dotenv(BACKEND_DIR / ".env")
load_dotenv(REPO_ROOT / ".env")


def _normalize_supabase_url(url: str | None) -> str | None:
    if not url:
        return url
    return url.rstrip("/").removesuffix("/rest/v1")


SUPABASE_URL = _normalize_supabase_url(os.getenv("SUPABASE_URL"))
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")
