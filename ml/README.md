# ML Module

AI/ML pipeline for the BTC Trading Analysis Platform.

## Setup

1. `python -m venv .venv`
2. Activate it (`source .venv/Scripts/activate` on Git Bash, `.venv\Scripts\activate` on Windows)
3. `pip install -r requirements.txt`
4. Put `SUPABASE_URL`, `SUPABASE_SECRET_KEY` and `GROQ_API_KEY` in the repo-root `.env` (never commit it)

Run everything from inside `ml/` with `python -m <module>`.

## Pipeline

| Command | What it does |
|---|---|
| `python -m train` | Fetches 180 days of hourly BTC data, builds features, trains RandomForest and XGBoost, saves XGBoost to `models/` plus `metrics.json` (macro F1, accuracy) |
| `python -m validate` | Scores the saved model on the last 14 days |
| `python -m predict` | Latest closed-candle signal in the API contract shape |
| `python -m backtest` | Backtests the 4 rule-based strategies (return, win rate, Sharpe, max drawdown) |
| `python -m explainer` | LLM-generated pros/cons per strategy (Groq), cached in `strategy_explanations.json` |
| `python -m update_strategy_explanations` | Writes pros/cons into the Supabase `strategies` table |
| `python -m update_backtest_results` | Writes backtest results into `backtest_results` |
| `python -m update_signals` | Writes the latest signal into `signals` |

## Files

- `data.py`: Binance klines (base URL from `BINANCE_BASE_URL`)
- `indicators/`: RSI, MACD, SMA/EMA, Bollinger Bands
- `features.py`: indicators plus scale-free features
- `labels.py`: BUY/HOLD/SELL labels from future price movement
- `strategies.py`: 5 strategies with Python rules and structured `buy_criteria`/`sell_criteria`
- `train.py`, `predict.py`, `validate.py`, `backtest.py`, `explainer.py`, `update_*.py`

## Model status

- XGBoost with 12 scale-free features. Raw price-level features were removed because they made predictions collapse to one class on recent data.
- Chronological 80/20 split. Macro F1 is about 0.30 on the test set and about 0.31 on the last 14 days.
- Honest limitation: the model shows no demonstrated edge on BUY/SELL beyond the class mix, and `confidence` is not a calibrated probability.
- Backtests don't include fees or slippage, and results shift with the data window.

## Output contract

Matches `/api/signals/btc`:

```json
{"symbol": "BTC", "signal": "HOLD", "confidence": 0.78, "timestamp": 1792731600}
```