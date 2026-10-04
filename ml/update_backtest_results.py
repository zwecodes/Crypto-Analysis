"""
Writes backtest results for all rule-based strategies into the
Supabase backtest_results table.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
from backtest import run_all_backtests

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

if SUPABASE_URL and SUPABASE_URL.endswith("/rest/v1/"):
    SUPABASE_URL = SUPABASE_URL.removesuffix("/rest/v1/")


def _client():
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SECRET_KEY")
    return create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)


def write_backtest_results() -> int:
    results = run_all_backtests()
    client = _client()
    written = 0

    for result in results:
        row = {
            "strategy_id": result["strategy_id"],
            "start_date": result["start_date"],
            "end_date": result["end_date"],
            "total_return_pct": result["total_return_pct"],
            "win_rate_pct": result["win_rate_pct"],
            "num_trades": result["num_trades"],
            "trades": result["trades"],
        }

        (
            client.table("backtest_results")
            .upsert(row, on_conflict="strategy_id,start_date,end_date")
            .execute()
        )
        print(f"Wrote backtest results for {result['strategy_id']} "
              f"({result['start_date']} to {result['end_date']})")
        written += 1

    return written


if __name__ == "__main__":
    try:
        count = write_backtest_results()
        print(f"\nDone. Wrote {count} backtest result row(s).")
    except Exception as exc:
        print(f"Write failed: {exc}")
        sys.exit(1)