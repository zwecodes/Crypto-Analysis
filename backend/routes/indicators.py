from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from supabase import create_client

from config import SUPABASE_SECRET_KEY, SUPABASE_URL

router = APIRouter(prefix="/api/indicators", tags=["indicators"])

SYMBOL = "BTC"


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


def _get_client():
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SECRET_KEY")
    return create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)


def _optional_float(value):
    if value is None:
        return None
    return float(value)


def _serialize_indicator(row: dict) -> dict:
    return {
        "timestamp": int(row["timestamp"]),
        "rsi": _optional_float(row.get("rsi")),
        "macd": _optional_float(row.get("macd")),
        "macd_signal": _optional_float(row.get("macd_signal")),
        "sma_20": _optional_float(row.get("sma_20")),
        "sma_50": _optional_float(row.get("sma_50")),
    }


@router.get("/btc")
def get_btc_indicators(
    interval: str = Query("1h"),
    limit: int = Query(200),
    offset: int = Query(0),
):
    if not interval.strip():
        return _error(400, "BAD_REQUEST", "interval must not be empty")
    if limit < 1:
        return _error(400, "BAD_REQUEST", "limit must be greater than 0")
    if offset < 0:
        return _error(400, "BAD_REQUEST", "offset must be greater than or equal to 0")

    try:
        response = (
            _get_client()
            .table("indicators")
            .select("timestamp, rsi, macd, macd_signal, sma_20, sma_50")
            .eq("symbol", SYMBOL)
            .eq("interval", interval)
            .order("timestamp", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
    except Exception as exc:
        return _error(500, "INTERNAL_ERROR", str(exc))

    indicators = [_serialize_indicator(row) for row in (response.data or [])]
    return {"symbol": SYMBOL, "interval": interval, "indicators": indicators}
