"""
Re-validates the saved XGBoost model on the most recent data.
"""

import joblib
from sklearn.metrics import classification_report, f1_score
from data import get_btc_data_extended
from features import build_feature_dataframe
from labels import add_labels
from train import FEATURE_COLUMNS
from sklearn.metrics import classification_report, confusion_matrix, f1_score

def validate_recent(recent_days: int = 14):
    model = joblib.load("models/baseline_xgb.pkl")
    label_map = joblib.load("models/label_map.pkl")

    df = get_btc_data_extended(days_back=180)
    df = build_feature_dataframe(df)
    df = add_labels(df)
    df = df.dropna(subset=FEATURE_COLUMNS + ["label"])

    recent = df.tail(recent_days * 24)  # hourly candles
    y_true = recent["label"].map(label_map)
    y_pred = model.predict(recent[FEATURE_COLUMNS])

    print(f"Validated on the last {recent_days} days ({len(recent)} rows)")
    print(f"From {recent['open_time'].iloc[0]} to {recent['open_time'].iloc[-1]}")
    print(f"Accuracy: {(y_pred == y_true.values).mean():.3f}")
    print(f"Macro F1: {f1_score(y_true, y_pred, average='macro'):.3f}")
    print(classification_report(
        y_true, y_pred,
        labels=[0, 1, 2],
        target_names=["BUY", "HOLD", "SELL"],
        zero_division=0,
    ))
    print("Confusion matrix (rows = actual BUY/HOLD/SELL, cols = predicted):")
    print(confusion_matrix(y_true, y_pred, labels=[0, 1, 2]))


if __name__ == "__main__":
    validate_recent()