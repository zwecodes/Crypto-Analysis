from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from supabase import create_client

from config import SUPABASE_SECRET_KEY, SUPABASE_URL
from services.auth import get_current_user

router = APIRouter(prefix="/api/user", tags=["user"])

_EMPTY_STRATEGY = {
    "strategy_id": None,
    "active": False,
    "selected_at": None,
}


class StrategySelectRequest(BaseModel):
    strategy_id: str


def _http_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message},
    )


def _get_client():
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SECRET_KEY")
    return create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)


def _iso_z(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc).replace(microsecond=0)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _serialize(row: dict) -> dict:
    return {
        "strategy_id": row.get("strategy_id"),
        "active": bool(row.get("active")),
        "selected_at": _iso_z(row.get("selected_at")),
    }


def _fetch_row(client, user_id: str) -> dict | None:
    response = (
        client.table("user_strategy")
        .select("strategy_id, active, selected_at")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


@router.get("/strategy")
def get_user_strategy(user_id: str = Depends(get_current_user)):
    try:
        row = _fetch_row(_get_client(), user_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise _http_error(500, "INTERNAL_ERROR", str(exc)) from exc

    if not row or not row.get("active"):
        return _EMPTY_STRATEGY
    return _serialize(row)


@router.post("/strategy")
def select_user_strategy(
    body: StrategySelectRequest,
    user_id: str = Depends(get_current_user),
):
    strategy_id = body.strategy_id.strip()
    if not strategy_id:
        raise _http_error(400, "BAD_REQUEST", "strategy_id must not be empty")

    selected_at = datetime.now(timezone.utc).replace(microsecond=0)

    try:
        client = _get_client()
        existing = (
            client.table("strategies")
            .select("id")
            .eq("id", strategy_id)
            .limit(1)
            .execute()
        )
        if not existing.data:
            raise _http_error(
                404, "NOT_FOUND", f"Strategy '{strategy_id}' not found"
            )

        response = (
            client.table("user_strategy")
            .upsert(
                {
                    "user_id": user_id,
                    "strategy_id": strategy_id,
                    "active": True,
                    "selected_at": selected_at.isoformat(),
                },
                on_conflict="user_id",
                default_to_null=False,
            )
            .execute()
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise _http_error(500, "INTERNAL_ERROR", str(exc)) from exc

    rows = response.data or []
    if rows:
        return _serialize(rows[0])
    return {
        "strategy_id": strategy_id,
        "active": True,
        "selected_at": _iso_z(selected_at),
    }


@router.delete("/strategy")
def deselect_user_strategy(user_id: str = Depends(get_current_user)):
    try:
        (
            _get_client()
            .table("user_strategy")
            .update({"active": False})
            .eq("user_id", user_id)
            .execute()
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise _http_error(500, "INTERNAL_ERROR", str(exc)) from exc

    return Response(status_code=204)
