"""
Bollinger Bands — volatility bands around a moving average.
"""

import pandas as pd


def compute_bollinger(df: pd.DataFrame, period: int = 20, num_std: int = 2) -> pd.DataFrame:
    sma = df["close"].rolling(window=period).mean()
    std = df["close"].rolling(window=period).std()

    df["bb_middle"] = sma
    df["bb_upper"] = sma + (num_std * std)
    df["bb_lower"] = sma - (num_std * std)

    return df


if __name__ == "__main__":
    from data import get_btc_data
    df = get_btc_data()
    df = compute_bollinger(df)
    print(df[["open_time", "close", "bb_lower", "bb_middle", "bb_upper"]].tail())