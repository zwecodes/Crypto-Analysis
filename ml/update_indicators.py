"""
Writes the latest indicator values (RSI, MACD, SMA, EMA, Bollinger Bands) into
the Supabase indicators table so the dashboard cards can show real values.
Upserts on (symbol, interval, timestamp), so re-running never creates duplicates.

Run from ml/:
    python -m update_indicators --dry-run     # show what would be written, no DB access
    python -m update_indicators               # write the latest 200 candles
    python -m update_indicators --rows 500
"""

import argparse
import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from data import get_btc_data
from indicators.macd import compute_macd
from indicators.moving_averages import compute_sma
from indicators.rsi import compute_rsi

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

if SUPABASE_URL and SUPABASE_URL.endswith("/rest/v1/"):
    SUPABASE_URL = SUPABASE_URL.removesuffix("/rest/v1/")

SYMBOL = "BTC"
INTERVAL = "1h"

# Columns that exist in the Supabase indicators table (besides id, symbol,
# interval, timestamp, created_at). EMA, MACD histogram and Bollinger Bands
# are not stored, so they are not written.
TABLE_COLS = ["rsi", "macd", "macd_signal", "sma_20", "sma_50"]


def _client():
    from supabase import create_client

    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SECRET_KEY")
    return create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)


def _unix_seconds(df: pd.DataFrame) -> pd.Series:
    """Candle time as unix seconds (same unit as the signals table)."""
    for name in ("timestamp", "open_time", "time", "date"):
        if name in df.columns:
            s = df[name]
            break
    else:
        s = df.index.to_series()
    if pd.api.types.is_numeric_dtype(s):
        s = s.astype("int64")
        return s // 1000 if s.max() > 10**11 else s
    s = pd.to_datetime(s, utc=True)
    return (s - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta(seconds=1)


def build_rows(limit: int = 1000, rows: int = 200):
    df = get_btc_data(interval=INTERVAL, limit=limit)
    df = df.iloc[:-1]
    base_cols = list(df.columns)
    ts = _unix_seconds(df)
    sma50 = compute_sma(df, period=50)
    sma50_cols = [c for c in sma50.columns if c not in base_cols]
    if not sma50_cols:
        raise RuntimeError("compute_sma(period=50) added no column")
    for fn in (compute_rsi, compute_macd, compute_sma):
        df = fn(df)
    detected = [c for c in df.columns if c not in base_cols]
    df["sma_50"] = sma50[sma50_cols[0]].values
    missing = [c for c in TABLE_COLS if c not in df.columns]
    if missing:
        raise RuntimeError(
            f"Indicator columns missing: {missing}. Detected: {detected}"
        )
    out = df[TABLE_COLS].copy()
    out["timestamp"] = ts.values
    out = out.dropna().tail(rows)
    records = []
    for rec in out.to_dict(orient="records"):
        row = {
            "symbol": SYMBOL,
            "interval": INTERVAL,
            "timestamp": int(rec.pop("timestamp")),
        }
        row.update({k: round(float(v), 4) for k, v in rec.items()})
        records.append(row)
    return detected, records


def write_indicators(rows: int = 200) -> int:
    _, records = build_rows(rows=rows)
    client = _client()
    for i in range(0, len(records), 500):
        client.table("indicators").upsert(
            records[i : i + 500], on_conflict="symbol,interval,timestamp"
        ).execute()
    return len(records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--rows", type=int, default=200)
    args = parser.parse_args()
    try:
        if args.dry_run:
            cols, records = build_rows(rows=args.rows)
            print(f"Detected indicator columns: {cols}")
            print(f"Rows ready: {len(records)}")
            print(f"Latest row: {records[-1]}")
        else:
            n = write_indicators(rows=args.rows)
            print(f"Wrote {n} indicator rows")
    except Exception as exc:
        print(f"Indicator write failed: {exc}")
        sys.exit(1)