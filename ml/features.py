"""
Combines all indicators into a single feature-ready DataFrame.
"""

from data import get_btc_data
from indicators.rsi import compute_rsi
from indicators.macd import compute_macd
from indicators.moving_averages import compute_sma, compute_ema
from indicators.bollinger import compute_bollinger


def build_feature_dataframe(df=None):
    if df is None:
        df = get_btc_data()

    df = compute_rsi(df)
    df = compute_macd(df)
    df = compute_sma(df, 20)
    df = compute_sma(df, 50)
    df = compute_ema(df, 20)
    df = compute_bollinger(df)

    # Lagged features — value from a few periods ago
    df["rsi_lag1"] = df["rsi"].shift(1)
    df["macd_lag1"] = df["macd"].shift(1)

    # Rate of change — how fast is the indicator moving
    df["rsi_roc"] = df["rsi"].diff()
    df["close_roc"] = df["close"].pct_change()

    return df


if __name__ == "__main__":
    df = build_feature_dataframe()
    print(df.tail())
    print(f"\nColumns: {list(df.columns)}")
