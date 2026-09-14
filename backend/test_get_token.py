"""Dev-only: sign in and print a Supabase access token for testing protected routes.

Usage (from /backend):
    python test_get_token.py

Requires TEST_USER_EMAIL and TEST_USER_PASSWORD in the environment or .env.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

BACKEND_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_DIR.parent

load_dotenv(BACKEND_DIR / ".env")
load_dotenv(REPO_ROOT / ".env")

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from config import SUPABASE_SECRET_KEY, SUPABASE_URL


def main() -> int:
    email = os.getenv("TEST_USER_EMAIL")
    password = os.getenv("TEST_USER_PASSWORD")
    if not email or not password:
        print("Missing TEST_USER_EMAIL or TEST_USER_PASSWORD")
        return 1

    if not SUPABASE_URL:
        print("Missing SUPABASE_URL")
        return 1

    api_key = os.getenv("SUPABASE_PUBLISHABLE_KEY") or SUPABASE_SECRET_KEY
    if not api_key:
        print("Missing SUPABASE_PUBLISHABLE_KEY or SUPABASE_SECRET_KEY")
        return 1

    try:
        client = create_client(SUPABASE_URL, api_key)
        response = client.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
    except Exception as exc:
        print(f"Sign-in failed: {exc}")
        return 1

    session = getattr(response, "session", None)
    token = getattr(session, "access_token", None) if session is not None else None
    if not token:
        print("Sign-in succeeded but no access_token was returned")
        return 1

    print(token)
    return 0


if __name__ == "__main__":
    sys.exit(main())
