"""
Loads the saved model and predicts on the latest data.
"""

import joblib
from features import build_feature_dataframe
from train import FEATURE_COLUMNS


def predict_latest():
    model = joblib.load("models/baseline_rf.pkl")
    df = build_feature_dataframe()
    df = df.dropna(subset=FEATURE_COLUMNS)

    latest = df.iloc[[-1]]  # most recent row only
    prediction = model.predict(latest[FEATURE_COLUMNS])[0]
    confidence = model.predict_proba(latest[FEATURE_COLUMNS]).max()

    return {
        "timestamp": str(latest["open_time"].values[0]),
        "signal": prediction,
        "confidence": round(float(confidence), 3),
    }


if __name__ == "__main__":
    result = predict_latest()
    print(result)