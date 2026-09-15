"""Fetch BTC OHLCV candles from Binance and upsert them into Supabase prices."""

import sys
from pathlib import Path

import httpx
from supabase import create_client

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from config import SUPABASE_SECRET_KEY, SUPABASE_URL

BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"
BINANCE_SYMBOL = "BTCUSDT"
DB_SYMBOL = "BTC"
INTERVAL = "1h"
LIMIT = 500


def fetch_binance_klines() -> list:
    try:
        response = httpx.get(
            BINANCE_KLINES_URL,
            params={
                "symbol": BINANCE_SYMBOL,
                "interval": INTERVAL,
                "limit": LIMIT,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Binance request failed: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError(f"Binance response was not valid JSON: {exc}") from exc

    if not isinstance(data, list):
        raise RuntimeError(f"Unexpected Binance response shape: {type(data).__name__}")

    return data


def parse_candles(raw_klines: list) -> list[dict]:
    candles = []
    for i, kline in enumerate(raw_klines):
        try:
            candles.append(
                {
                    "symbol": DB_SYMBOL,
                    "interval": INTERVAL,
                    "timestamp": int(kline[0]) // 1000,
                    "open": float(kline[1]),
                    "high": float(kline[2]),
                    "low": float(kline[3]),
                    "close": float(kline[4]),
                    "volume": float(kline[5]),
                }
            )
        except (TypeError, ValueError, IndexError) as exc:
            raise RuntimeError(f"Failed to parse Binance candle at index {i}: {exc}") from exc
    return candles


def upsert_prices(candles: list[dict]) -> int:
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SECRET_KEY in environment")

    if not candles:
        return 0

    try:
        client = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
        response = (
            client.table("prices")
            .upsert(candles, on_conflict="symbol,interval,timestamp")
            .execute()
        )
    except Exception as exc:
        raise RuntimeError(f"Supabase write failed: {exc}") from exc

    return len(response.data or [])


def run_pipeline() -> int:
    raw_klines = fetch_binance_klines()
    candles = parse_candles(raw_klines)
    return upsert_prices(candles)


if __name__ == "__main__":
    try:
        count = run_pipeline()
        print(f"Upserted {count} BTC {INTERVAL} candle(s) into prices.")
    except Exception as exc:
        print(f"Data pipeline failed: {exc}")
        sys.exit(1)
