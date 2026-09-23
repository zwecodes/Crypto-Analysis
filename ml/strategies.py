"""
Predefined trading strategies — rule-based definitions used for
backtesting and later for the alert system.
"""

STRATEGIES = [
    {
        "id": "rsi_oversold",
        "name": "RSI Oversold/Overbought",
        "description": "Buys when RSI < 30, sells when RSI > 70",
        "buy_rule": lambda row: row["rsi"] < 30,
        "sell_rule": lambda row: row["rsi"] > 70,
    },
    {
        "id": "ma_crossover",
        "name": "Moving Average Crossover",
        "description": "Buys when the 20-period EMA crosses above the 50-period SMA, sells on the reverse",
        "buy_rule": lambda row: row["ema_20"] > row["sma_50"],
        "sell_rule": lambda row: row["ema_20"] < row["sma_50"],
    },
    {
        "id": "macd_momentum",
        "name": "MACD Momentum",
        "description": "Buys when MACD crosses above its signal line, sells on the reverse",
        "buy_rule": lambda row: row["macd"] > row["macd_signal"],
        "sell_rule": lambda row: row["macd"] < row["macd_signal"],
    },
    {
        "id": "bollinger_bounce",
        "name": "Bollinger Band Bounce",
        "description": "Buys when price touches the lower band, sells when it touches the upper band",
        "buy_rule": lambda row: row["close"] <= row["bb_lower"],
        "sell_rule": lambda row: row["close"] >= row["bb_upper"],
    },
    {
        "id": "ml_signal",
        "name": "ML Model Signal",
        "description": "Uses the trained XGBoost classifier's BUY/HOLD/SELL prediction directly",
        "buy_rule": None,  # handled separately via predict.py, not a simple row-based rule
        "sell_rule": None,
    },
]


def get_strategy(strategy_id):
    for s in STRATEGIES:
        if s["id"] == strategy_id:
            return s
    raise ValueError(f"Unknown strategy: {strategy_id}")


if __name__ == "__main__":
    for s in STRATEGIES:
        print(f"{s['id']}: {s['name']} — {s['description']}")
