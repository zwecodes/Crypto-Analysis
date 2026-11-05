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


def _iso_date(value) -> str:
    text = str(value).strip()
    if len(text) >= 10 and text[4] == "-" and text[7] == "-":
        return text[:10]
    return text


def _serialize_trade(trade: dict) -> dict:
    return {
        "entry_date": _iso_date(trade.get("entry_date")),
        "exit_date": _iso_date(trade.get("exit_date")),
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


NO_MATCHING_BACKTEST = "NO_MATCHING_BACKTEST"


def _available_ranges(client, strategy_id: str, limit: int = 3) -> list[tuple[str, str]]:
    """Newest cached (start_date, end_date) windows for a strategy, for the error message."""
    try:
        rows = (
            client.table("backtest_results")
            .select("start_date, end_date")
            .eq("strategy_id", strategy_id)
            .order("computed_at", desc=True)
            .limit(limit)
            .execute()
        ).data or []
    except Exception:
        return []  # never turn a clean "no match" into a 500 just for the hint

    ranges: list[tuple[str, str]] = []
    for row in rows:
        pair = (_iso_date(row["start_date"]), _iso_date(row["end_date"]))
        if pair not in ranges:
            ranges.append(pair)
    return ranges


def _no_match_message(client, strategy_id: str, start: date, end: date) -> str:
    message = (
        f"No backtest result for '{strategy_id}' from "
        f"{start.isoformat()} to {end.isoformat()}."
    )
    ranges = _available_ranges(client, strategy_id)
    if not ranges:
        return message + " No backtest results have been computed for this strategy yet."
    listed = "; ".join(f"{a} to {b}" for a, b in ranges)
    return f"{message} Available ranges: {listed}."


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

        # Look up the cached result for exactly this window.
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

        # Only an exact match on the requested window is returned. A different
        # window must never be returned silently (the frontend would show a
        # date range the user did not select).
        raise _http_error(
            404,
            NO_MATCHING_BACKTEST,
            _no_match_message(client, strategy_id, start, end),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise _http_error(500, "INTERNAL_ERROR", str(exc)) from exc