"""
Loads the saved XGBoost model and predicts on the latest data,
outputting in the shared signals contract format.
"""

import json
import joblib
from features import build_feature_dataframe
from train import FEATURE_COLUMNS


def predict_latest():
    model = joblib.load("models/baseline_xgb.pkl")
    label_map = joblib.load("models/label_map.pkl")
    reverse_map = {v: k for k, v in label_map.items()}

    df = build_feature_dataframe()
    df = df.dropna(subset=FEATURE_COLUMNS)

    latest = df.iloc[[-1]]
    prediction_numeric = model.predict(latest[FEATURE_COLUMNS])[0]
    prediction = reverse_map[prediction_numeric]

    confidence = model.predict_proba(latest[FEATURE_COLUMNS]).max()

    timestamp = int(
        latest["open_time"].values[0].astype("datetime64[s]").astype("int64")
    )

    signal_output = {
        "symbol": "BTC",
        "signal": prediction,
        "confidence": round(float(confidence), 2),
        "timestamp": timestamp,
    }
    return signal_output


def save_signal_to_file(signal, path="signals_output.json"):
    """Temporary local output until DB write is wired up with Backend."""
    with open(path, "w") as f:
        json.dump(signal, f, indent=2)


if __name__ == "__main__":
    result = predict_latest()
    print(json.dumps(result, indent=2))
    save_signal_to_file(result)
    print("\nSaved to signals_output.json")
