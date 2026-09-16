from fastapi import APIRouter
from fastapi.responses import JSONResponse
from supabase import create_client

from config import SUPABASE_SECRET_KEY, SUPABASE_URL

router = APIRouter(prefix="/api/signals", tags=["signals"])

SYMBOL = "BTC"

_EMPTY_SIGNAL = {
    "symbol": SYMBOL,
    "signal": "HOLD",
    "confidence": None,
    "timestamp": None,
}


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


def _get_client():
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SECRET_KEY")
    return create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)


@router.get("/btc")
def get_btc_signal():
    try:
        response = (
            _get_client()
            .table("signals")
            .select("symbol, signal, confidence, timestamp")
            .eq("symbol", SYMBOL)
            .order("timestamp", desc=True)
            .limit(1)
            .execute()
        )
    except Exception as exc:
        return _error(500, "INTERNAL_ERROR", str(exc))

    rows = response.data or []
    if not rows:
        return _EMPTY_SIGNAL

    row = rows[0]
    confidence = row.get("confidence")
    return {
        "symbol": row.get("symbol") or SYMBOL,
        "signal": row["signal"],
        "confidence": float(confidence) if confidence is not None else None,
        "timestamp": int(row["timestamp"]),
    }
