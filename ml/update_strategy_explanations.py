"""
Updates the pros/cons columns on existing strategy rows in Supabase.
Does NOT touch id, name, or description — those are owned by
backend/services/seed_strategies.py.

Run once, after ml/explainer.py has generated strategy_explanations.json.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

if SUPABASE_URL and SUPABASE_URL.endswith("/rest/v1/"):
    SUPABASE_URL = SUPABASE_URL.removesuffix("/rest/v1/")

EXPLANATIONS_PATH = Path(__file__).parent / "strategy_explanations.json"


def _client():
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SECRET_KEY")
    return create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)


def update_strategy_pros_cons() -> int:
    if not EXPLANATIONS_PATH.exists():
        raise FileNotFoundError(
            f"{EXPLANATIONS_PATH} not found — run `python -m explainer` first."
        )

    with open(EXPLANATIONS_PATH) as f:
        explanations = json.load(f)

    client = _client()
    updated = 0

    for item in explanations:
        strategy_id = item["strategy_id"]
        pros = item.get("pros", [])
        cons = item.get("cons", [])

        if not pros and not cons:
            print(f"Skipping {strategy_id} — no pros/cons to write (likely a failed LLM call).")
            continue

        (
            client.table("strategies")
            .update({"pros": pros, "cons": cons})
            .eq("id", strategy_id)
            .execute()
        )
        print(f"Updated {strategy_id}")
        updated += 1

    return updated


if __name__ == "__main__":
    try:
        count = update_strategy_pros_cons()
        print(f"\nDone. Updated {count} strategy row(s).")
    except Exception as exc:
        print(f"Update failed: {exc}")
        sys.exit(1)