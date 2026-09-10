"""
Simple and Exponential Moving Averages.
"""

import pandas as pd


def compute_sma(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    df[f"sma_{period}"] = df["close"].rolling(window=period).mean()
    return df


def compute_ema(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    df[f"ema_{period}"] = df["close"].ewm(span=period, adjust=False).mean()
    return df


if __name__ == "__main__":
    from data import get_btc_data
    df = get_btc_data()
    df = compute_sma(df, 20)
    df = compute_sma(df, 50)
    df = compute_ema(df, 20)
    print(df[["open_time", "close", "sma_20", "sma_50", "ema_20"]].tail())