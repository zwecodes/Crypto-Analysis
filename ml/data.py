"""
Day 5 starter: fetch real BTC candlestick data from Binance's public API.
No API key needed for this endpoint.
"""

import requests
import os
import pandas as pd
from datetime import *

BINANCE_BASE_URL = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")

def get_btc_data(interval: str = "1h", limit: int = 1000) -> pd.DataFrame:
    """
    Fetch historical BTC/USDT candlestick data from Binance.

    Args:
        interval: candle size, e.g. "1m", "5m", "1h", "1d"
        limit: number of candles to fetch (max 1000 per Binance's API)

    Returns:
        DataFrame with columns: open_time, open, high, low, close, volume
    """
    url = f"{BINANCE_BASE_URL}/api/v3/klines"
    params = {"symbol": "BTCUSDT", "interval": interval, "limit": limit}

    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()  # raises an error if the request failed
    data = resp.json()

    df = pd.DataFrame(
        data,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "trades",
            "taker_buy_base",
            "taker_buy_quote",
            "ignore",
        ],
    )

    # Convert types — Binance returns everything as strings
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")

    return df[["open_time", "open", "high", "low", "close", "volume"]]


def get_btc_data_extended(interval: str = "1h", days_back: int = 180) -> pd.DataFrame:
    """
    Fetch a large historical range by paginating backwards in time.
    Binance limits 1000 candles per request, so we loop.
    """
    url = f"{BINANCE_BASE_URL}/api/v3/klines"
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = int((datetime.now() - timedelta(days=days_back)).timestamp() * 1000)

    all_candles = []
    current_end = end_time

    while current_end > start_time:
        params = {
            "symbol": "BTCUSDT",
            "interval": interval,
            "limit": 1000,
            "endTime": current_end,
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if not data:
            break

        all_candles = data + all_candles
        current_end = (
            data[0][0] - 1
        )  # move window back before the earliest candle received

    df = pd.DataFrame(
        all_candles,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "trades",
            "taker_buy_base",
            "taker_buy_quote",
            "ignore",
        ],
    )

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df = df.drop_duplicates(subset="open_time").reset_index(drop=True)

    return df[["open_time", "open", "high", "low", "close", "volume"]]


if __name__ == "__main__":
    # Quick manual test — run this file directly to sanity-check the fetch works
    df = get_btc_data()
    print(df.tail())
    print(f"\nFetched {len(df)} rows.")
