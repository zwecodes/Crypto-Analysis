"""
Day 6 starter: RSI (Relative Strength Index).
Measures momentum — values above 70 are often considered "overbought",
below 30 "oversold".
"""

import pandas as pd


def compute_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    return df


if __name__ == "__main__":
    from ml.data import get_btc_data
    df = get_btc_data()
    df = compute_rsi(df)
    print(df[["open_time", "close", "rsi"]].tail())
