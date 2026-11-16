"""
Writes backtest results for all rule-based strategies into the
Supabase backtest_results table.

    python -m update_backtest_results                # every end date from the fixed start date
    python -m update_backtest_results --latest-only  # old behaviour: one window ending on the newest candle

Upserts on (strategy_id, start_date, end_date), so re-running never creates duplicates.
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
from backtest import run_all_backtests, run_backtests_for_end_dates

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

if SUPABASE_URL and SUPABASE_URL.endswith("/rest/v1/"):
    SUPABASE_URL = SUPABASE_URL.removesuffix("/rest/v1/")

BATCH_SIZE = 20


def _client():
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SECRET_KEY")
    return create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)


def _to_row(result: dict) -> dict:
    return {
        "strategy_id": result["strategy_id"],
        "start_date": result["start_date"],
        "end_date": result["end_date"],
        "total_return_pct": result["total_return_pct"],
        "win_rate_pct": result["win_rate_pct"],
        "num_trades": result["num_trades"],
        "trades": result["trades"],
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }


def write_backtest_results(latest_only: bool = False) -> int:
    results = run_all_backtests() if latest_only else run_backtests_for_end_dates()
    rows = [_to_row(r) for r in results]
    client = _client()
    written = 0

    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        (
            client.table("backtest_results")
            .upsert(batch, on_conflict="strategy_id,start_date,end_date")
            .execute()
        )
        written += len(batch)
        print(f"  wrote {written}/{len(rows)}")

    return written


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--latest-only", action="store_true")
    args = parser.parse_args()
    try:
        count = write_backtest_results(latest_only=args.latest_only)
        print(f"\nDone. Wrote {count} backtest result row(s).")
    except Exception as exc:
        print(f"Write failed: {exc}")
        sys.exit(1)