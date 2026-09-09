from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from supabase import create_client

from config import SUPABASE_SECRET_KEY, SUPABASE_URL

router = APIRouter(prefix="/api/prices", tags=["prices"])

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


def _serialize_candle(row: dict) -> dict:
    return {
        "timestamp": int(row["timestamp"]),
        "open": float(row["open"]),
        "high": float(row["high"]),
        "low": float(row["low"]),
        "close": float(row["close"]),
        "volume": float(row["volume"]),
    }


@router.get("/btc")
def get_btc_prices(
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
        client = _get_client()
        response = (
            client.table("prices")
            .select("timestamp, open, high, low, close, volume")
            .eq("symbol", SYMBOL)
            .eq("interval", interval)
            .order("timestamp", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
    except Exception as exc:
        return _error(500, "INTERNAL_ERROR", str(exc))

    candles = [_serialize_candle(row) for row in (response.data or [])]
    return {"symbol": SYMBOL, "interval": interval, "candles": candles}
