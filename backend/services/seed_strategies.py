"""Insert the five predefined strategies into Supabase.

Names and descriptions match ml/strategies.py. Existing pros/cons are left
alone so the AI explainer can fill them without this script wiping them.
"""

import sys
from pathlib import Path

from supabase import create_client

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from config import SUPABASE_SECRET_KEY, SUPABASE_URL

STRATEGIES = [
    {
        "id": "rsi_oversold",
        "name": "RSI Oversold/Overbought",
        "description": "Buys when RSI < 30, sells when RSI > 70",
    },
    {
        "id": "ma_crossover",
        "name": "Moving Average Crossover",
        "description": "Buys when the 20-period EMA crosses above the 50-period SMA, sells on the reverse",
    },
    {
        "id": "macd_momentum",
        "name": "MACD Momentum",
        "description": "Buys when MACD crosses above its signal line, sells on the reverse",
    },
    {
        "id": "bollinger_bounce",
        "name": "Bollinger Band Bounce",
        "description": "Buys when price touches the lower band, sells when it touches the upper band",
    },
    {
        "id": "ml_signal",
        "name": "ML Model Signal",
        "description": "Uses the trained XGBoost classifier's BUY/HOLD/SELL prediction directly",
    },
]


def _client():
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SECRET_KEY")
    return create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)


def seed_strategies() -> int:
    client = _client()
    existing = client.table("strategies").select("id").execute()
    existing_ids = {row["id"] for row in (existing.data or [])}

    inserted = 0
    for strategy in STRATEGIES:
        if strategy["id"] in existing_ids:
            (
                client.table("strategies")
                .update(
                    {
                        "name": strategy["name"],
                        "description": strategy["description"],
                    }
                )
                .eq("id", strategy["id"])
                .execute()
            )
            continue

        (
            client.table("strategies")
            .insert({**strategy, "pros": [], "cons": []})
            .execute()
        )
        inserted += 1

    return inserted


if __name__ == "__main__":
    try:
        count = seed_strategies()
        print(f"Seeded strategies. Inserted {count} new row(s).")
    except Exception as exc:
        print(f"Strategy seed failed: {exc}")
        sys.exit(1)
