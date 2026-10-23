"""
Writes the latest ML signal (last closed candle) into the Supabase signals table.
Upserts on (symbol, timestamp), so re-running never creates duplicates.
Run from ml/ (predict.py loads models/ with relative paths).
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
from predict import predict_latest

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


def write_latest_signal() -> dict:
    signal = predict_latest()
    row = {
        "symbol": signal["symbol"],
        "signal": signal["signal"],
        "confidence": signal["confidence"],
        "timestamp": signal["timestamp"],
    }
    _client().table("signals").upsert(row, on_conflict="symbol,timestamp").execute()
    return row


if __name__ == "__main__":
    try:
        row = write_latest_signal()
        print(f"Wrote signal: {row}")
    except Exception as exc:
        print(f"Signal write failed: {exc}")
        sys.exit(1)