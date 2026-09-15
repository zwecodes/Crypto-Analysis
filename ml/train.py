"""
Model training pipeline.
"""

import pandas as pd
from features import build_feature_dataframe
from labels import add_labels

FEATURE_COLUMNS = [
    "rsi",
    "macd",
    "macd_signal",
    "macd_histogram",
    "sma_20",
    "sma_50",
    "ema_20",
    "bb_middle",
    "bb_upper",
    "bb_lower",
]


def prepare_data():
    df = build_feature_dataframe()
    df = add_labels(df)
    df = df.dropna(subset=FEATURE_COLUMNS + ["label"])

    split_index = int(len(df) * 0.8)
    train_df = df.iloc[:split_index]
    test_df = df.iloc[split_index:]

    X_train, y_train = train_df[FEATURE_COLUMNS], train_df["label"]
    X_test, y_test = test_df[FEATURE_COLUMNS], test_df["label"]

    return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    X_train, X_test, y_train, y_test = prepare_data()
    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
    print(f"\nTrain label distribution:\n{y_train.value_counts()}")
    print(f"\nTest label distribution:\n{y_test.value_counts()}")
