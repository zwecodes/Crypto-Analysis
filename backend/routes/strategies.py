from fastapi import APIRouter
from fastapi.responses import JSONResponse
from supabase import create_client

from config import SUPABASE_SECRET_KEY, SUPABASE_URL
from services.seed_strategies import STRATEGIES

router = APIRouter(prefix="/api", tags=["strategies"])

_ORDER = [strategy["id"] for strategy in STRATEGIES]


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


def _get_client():
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SECRET_KEY")
    return create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)


def _as_string_list(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def serialize_strategy(row: dict) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "description": row["description"],
        "pros": _as_string_list(row.get("pros")),
        "cons": _as_string_list(row.get("cons")),
    }


@router.get("/strategies")
def list_strategies():
    try:
        response = (
            _get_client()
            .table("strategies")
            .select("id, name, description, pros, cons")
            .execute()
        )
    except Exception as exc:
        return _error(500, "INTERNAL_ERROR", str(exc))

    rows = response.data or []
    rows.sort(key=lambda row: _ORDER.index(row["id"]) if row["id"] in _ORDER else len(_ORDER))
    return {"strategies": [serialize_strategy(row) for row in rows]}
