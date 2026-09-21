"""
Model training pipeline.
"""

import joblib
import os
import pandas as pd
from features import build_feature_dataframe
from labels import add_labels
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import datetime
from xgboost import XGBClassifier
from sklearn.utils.class_weight import compute_sample_weight

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
    "rsi_lag1",
    "macd_lag1",
    "rsi_roc",
    "close_roc",
]


def prepare_data():
    # from data import get_btc_data

    # df = get_btc_data(limit=1000)
    # df = build_feature_dataframe()
    # df = add_labels(df)
    from data import get_btc_data_extended

    df = get_btc_data_extended(days_back=180)  # ~6 months of hourly data
    df = build_feature_dataframe(df)
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


# def train_xgboost_model(X_train, y_train):
#     # XGBoost needs numeric labels, not strings
#     label_map = {"BUY": 0, "HOLD": 1, "SELL": 2}
#     y_train_numeric = y_train.map(label_map)


#     model = XGBClassifier(
#         n_estimators=100,
#         max_depth=6,
#         learning_rate=0.1,
#         random_state=42,
#         eval_metric="mlogloss",
#     )
#     model.fit(X_train, y_train_numeric)
#     return model, label_map
def train_xgboost_model(X_train, y_train):
    label_map = {"BUY": 0, "HOLD": 1, "SELL": 2}
    y_train_numeric = y_train.map(label_map)

    sample_weights = compute_sample_weight(class_weight="balanced", y=y_train_numeric)

    model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric="mlogloss",
    )
    model.fit(X_train, y_train_numeric, sample_weight=sample_weights)
    return model, label_map


# if __name__ == "__main__":
#     X_train, X_test, y_train, y_test = prepare_data()
#     print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

#     model = train_model(X_train, y_train)
#     y_pred = model.predict(X_test)

#     print(f"\nAccuracy: {model.score(X_test, y_test):.3f}")
#     print("\nClassification report:")
#     print(classification_report(y_test, y_pred))
#     print("Confusion matrix (rows=actual, cols=predicted):")
#     print(confusion_matrix(y_test, y_pred, labels=["BUY", "HOLD", "SELL"]))

#     os.makedirs("models", exist_ok=True)
#     joblib.dump(model, "models/baseline_rf.pkl")
#     print("\nModel saved to models/baseline_rf.pkl")

if __name__ == "__main__":
    X_train, X_test, y_train, y_test = prepare_data()
    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

    print("\n=== RandomForest ===")
    rf_model = train_model(X_train, y_train)
    y_pred_rf = rf_model.predict(X_test)
    print(f"Accuracy: {rf_model.score(X_test, y_test):.3f}")
    print(classification_report(y_test, y_pred_rf))

    print("\n=== XGBoost ===")
    xgb_model, label_map = train_xgboost_model(X_train, y_train)
    reverse_map = {v: k for k, v in label_map.items()}
    y_test_numeric = y_test.map(label_map)
    y_pred_xgb_numeric = xgb_model.predict(X_test)
    y_pred_xgb = pd.Series(y_pred_xgb_numeric).map(reverse_map)

    accuracy_xgb = (y_pred_xgb_numeric == y_test_numeric.values).mean()
    print(f"Accuracy: {accuracy_xgb:.3f}")
    print(
        classification_report(
            y_test_numeric, y_pred_xgb_numeric, target_names=["BUY", "HOLD", "SELL"]
        )
    )

    os.makedirs("models", exist_ok=True)
    joblib.dump(xgb_model, "models/baseline_xgb.pkl")
    joblib.dump(label_map, "models/label_map.pkl")
    print("\nXGBoost model saved to models/baseline_xgb.pkl")
