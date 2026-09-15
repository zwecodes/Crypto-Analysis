"""
Model training pipeline.
"""

import pandas as pd
from features import build_feature_dataframe
from labels import add_labels
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

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
    from data import get_btc_data
    df = get_btc_data(limit=1000)
    df = build_feature_dataframe()
    df = add_labels(df)
    df = df.dropna(subset=FEATURE_COLUMNS + ["label"])

    split_index = int(len(df) * 0.8)
    train_df = df.iloc[:split_index]
    test_df = df.iloc[split_index:]

    X_train, y_train = train_df[FEATURE_COLUMNS], train_df["label"]
    X_test, y_test = test_df[FEATURE_COLUMNS], test_df["label"]

    return X_train, X_test, y_train, y_test


def train_model(X_train, y_train):
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)
    return model


if __name__ == "__main__":
    X_train, X_test, y_train, y_test = prepare_data()
    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

    model = train_model(X_train, y_train)
    y_pred = model.predict(X_test)

    print(f"\nAccuracy: {model.score(X_test, y_test):.3f}")
    print("\nClassification report:")
    print(classification_report(y_test, y_pred))
    print("Confusion matrix (rows=actual, cols=predicted):")
    print(confusion_matrix(y_test, y_pred, labels=["BUY", "HOLD", "SELL"]))
