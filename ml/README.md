# ML Module

AI/ML pipeline for the BTC Trading Analysis Platform — Saw Htet Arkar.

## Setup

1. `python -m venv .venv`
2. Activate it:
   - Windows: `.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`
3. `pip install -r requirements.txt`

## Run the full pipeline

1. `python -m train` — fetches live BTC data, builds features, trains the model, evaluates it, and saves it to `models/baseline_rf.pkl`
2. `python -m predict` — loads the saved model, predicts on the latest data, and outputs a signal matching the shared API contract (`symbol`, `signal`, `confidence`, `timestamp`)

## Files

- `data.py` — fetches live BTC OHLCV data from Binance
- `indicators/` — RSI, MACD, Moving Averages (SMA/EMA), Bollinger Bands
- `features.py` — combines all indicators into one model-ready feature set
- `labels.py` — labels historical rows BUY/HOLD/SELL based on future price movement
- `train.py` — chronological train/test split, trains a RandomForestClassifier, evaluates with precision/recall/F1 and a confusion matrix
- `predict.py` — loads the saved model and outputs the latest signal in the contract format

## Current model status (baseline)

- Accuracy varies run-to-run (roughly 35-45%) due to limited historical data size and crypto market volatility
- Class imbalance (HOLD dominates) addressed using `class_weight="balanced"`
- BUY recall is reasonably strong (~60%); SELL recall is still weak — documented limitation, candidate for improvement via more historical data and additional features (lagged/rate-of-change indicators)

## Output contract

Matches `/api/signals/btc` in the team's API contract doc:
```json
{
  "symbol": "BTC",
  "signal": "BUY",
  "confidence": 0.78,
  "timestamp": 1756339200
}
```