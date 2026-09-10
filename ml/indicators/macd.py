"""
MACD (Moving Average Convergence Divergence).
Measures momentum via the relationship between two EMAs.
"""

import pandas as pd


def compute_macd(df: pd.DataFrame, fast=12, slow=26, signal=9) -> pd.DataFrame:
    ema_fast = df["close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["close"].ewm(span=slow, adjust=False).mean()

    df["macd"] = ema_fast - ema_slow
    df["macd_signal"] = df["macd"].ewm(span=signal, adjust=False).mean()
    df["macd_histogram"] = df["macd"] - df["macd_signal"]

    return df


if __name__ == "__main__":
    from data import get_btc_data

    df = get_btc_data()
    df = compute_macd(df)
    print(df[["open_time", "close", "macd", "macd_signal", "macd_histogram"]].tail())
