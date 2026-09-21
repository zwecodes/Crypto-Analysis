from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Query
from supabase import create_client

from config import SUPABASE_SECRET_KEY, SUPABASE_URL

router = APIRouter(prefix="/api/backtest", tags=["backtest"])


def _http_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message},
    )


def _get_client():
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SECRET_KEY")
    return create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)


def _parse_iso_date(value: str | None, field_name: str) -> date | None:
    if value is None or value.strip() == "":
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError as exc:
        raise _http_error(
            400,
            "BAD_REQUEST",
            f"{field_name} must be an ISO date (YYYY-MM-DD)",
        ) from exc


def _default_date_range() -> tuple[date, date]:
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=182)  # ~6 months
    return start, end


def _optional_float(value):
    if value is None:
        return None
    return float(value)


def _serialize_trade(trade: dict) -> dict:
    return {
        "entry_date": str(trade.get("entry_date")),
        "exit_date": str(trade.get("exit_date")),
        "entry_price": float(trade["entry_price"]),
        "exit_price": float(trade["exit_price"]),
        "return_pct": float(trade["return_pct"]),
    }


def _serialize_row(row: dict) -> dict:
    trades_raw = row.get("trades") or []
    if not isinstance(trades_raw, list):
        trades_raw = []

    return {
        "strategy_id": row["strategy_id"],
        "start_date": str(row["start_date"]),
        "end_date": str(row["end_date"]),
        "total_return_pct": _optional_float(row.get("total_return_pct")),
        "win_rate_pct": _optional_float(row.get("win_rate_pct")),
        "num_trades": int(row["num_trades"] or 0),
        "trades": [_serialize_trade(t) for t in trades_raw if isinstance(t, dict)],
    }


def _empty_result(strategy_id: str, start: date, end: date) -> dict:
    return {
        "strategy_id": strategy_id,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "total_return_pct": None,
        "win_rate_pct": None,
        "num_trades": 0,
        "trades": [],
    }


@router.get("/{strategy_id}")
def get_backtest(
    strategy_id: str,
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
):
    strategy_id = strategy_id.strip()
    if not strategy_id:
        raise _http_error(400, "BAD_REQUEST", "strategy_id must not be empty")

    default_start, default_end = _default_date_range()
    start = _parse_iso_date(start_date, "start_date") or default_start
    end = _parse_iso_date(end_date, "end_date") or default_end

    if start > end:
        raise _http_error(
            400, "BAD_REQUEST", "start_date must be on or before end_date"
        )

    try:
        client = _get_client()

        strategy = (
            client.table("strategies")
            .select("id")
            .eq("id", strategy_id)
            .limit(1)
            .execute()
        )
        if not strategy.data:
            raise _http_error(
                404, "NOT_FOUND", f"Strategy '{strategy_id}' not found"
            )

        # Exact match on requested window first.
        exact = (
            client.table("backtest_results")
            .select(
                "strategy_id, start_date, end_date, "
                "total_return_pct, win_rate_pct, num_trades, trades"
            )
            .eq("strategy_id", strategy_id)
            .eq("start_date", start.isoformat())
            .eq("end_date", end.isoformat())
            .limit(1)
            .execute()
        )
        if exact.data:
            return _serialize_row(exact.data[0])

        # Fallback: newest cached result for this strategy (ML may use different windows).
        latest = (
            client.table("backtest_results")
            .select(
                "strategy_id, start_date, end_date, "
                "total_return_pct, win_rate_pct, num_trades, trades"
            )
            .eq("strategy_id", strategy_id)
            .order("computed_at", desc=True)
            .limit(1)
            .execute()
        )
        if latest.data:
            return _serialize_row(latest.data[0])

        return _empty_result(strategy_id, start, end)
    except HTTPException:
        raise
    except Exception as exc:
        raise _http_error(500, "INTERNAL_ERROR", str(exc)) from exc
