"""JWT auth dependency for protected FastAPI routes.

Example:
    from fastapi import APIRouter, Depends
    from services.auth import get_current_user

    router = APIRouter()

    @router.get("/api/example")
    def example(user_id: str = Depends(get_current_user)):
        return {"user_id": user_id}
"""

from fastapi import Header, HTTPException
from supabase import create_client

from config import SUPABASE_SECRET_KEY, SUPABASE_URL


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail={
            "code": "UNAUTHORIZED",
            "message": "Invalid or missing authentication token",
        },
    )


def _get_client():
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SECRET_KEY")
    return create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)


def get_current_user(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise _unauthorized()

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise _unauthorized()

    try:
        response = _get_client().auth.get_user(token)
        user = response.user
    except Exception:
        raise _unauthorized()

    if user is None or not getattr(user, "id", None):
        raise _unauthorized()

    return str(user.id)
