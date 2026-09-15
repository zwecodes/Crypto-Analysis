"""
Labels each row BUY/HOLD/SELL based on future price movement.
"""

import pandas as pd


def add_labels(df: pd.DataFrame, horizon: int = 4, threshold: float = 0.005) -> pd.DataFrame:
    """
    horizon: how many periods ahead to look (e.g. 4 hours ahead on 1h candles)
    threshold: % price change to count as BUY/SELL (0.005 = 0.5%)
    """
    future_price = df["close"].shift(-horizon)
    pct_change = (future_price - df["close"]) / df["close"]

    def label_row(change):
        if pd.isna(change):
            return None
        if change > threshold:
            return "BUY"
        elif change < -threshold:
            return "SELL"
        else:
            return "HOLD"

    df["label"] = pct_change.apply(label_row)
    return df


if __name__ == "__main__":
    from features import build_feature_dataframe
    df = build_feature_dataframe()
    df = add_labels(df)
    print(df[["open_time", "close", "label"]].tail(15))
    print("\nLabel counts:")
    print(df["label"].value_counts())