"""
Day 5 starter: fetch real BTC candlestick data from Binance's public API.
No API key needed for this endpoint.
"""

import requests
import pandas as pd


def get_btc_data(interval: str = "1h", limit: int = 500) -> pd.DataFrame:
    """
    Fetch historical BTC/USDT candlestick data from Binance.

    Args:
        interval: candle size, e.g. "1m", "5m", "1h", "1d"
        limit: number of candles to fetch (max 1000 per Binance's API)

    Returns:
        DataFrame with columns: open_time, open, high, low, close, volume
    """
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": "BTCUSDT", "interval": interval, "limit": limit}

    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()  # raises an error if the request failed
    data = resp.json()

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])

    # Convert types — Binance returns everything as strings
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")

    return df[["open_time", "open", "high", "low", "close", "volume"]]


if __name__ == "__main__":
    # Quick manual test — run this file directly to sanity-check the fetch works
    df = get_btc_data()
    print(df.tail())
    print(f"\nFetched {len(df)} rows.")
