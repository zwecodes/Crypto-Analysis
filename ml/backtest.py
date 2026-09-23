"""
Core backtesting engine — simulates a strategy's buy/sell rules
against historical data and tracks a hypothetical account balance.
"""

from features import build_feature_dataframe
from data import get_btc_data_extended
from strategies import get_strategy


def run_backtest(strategy_id: str, starting_balance: float = 10000.0):
    strategy = get_strategy(strategy_id)

    if strategy["buy_rule"] is None:
        raise NotImplementedError(
            f"Strategy '{strategy_id}' has no rule-based logic (likely the ML signal strategy) — "
            "backtest it separately using predict.py's model output instead."
        )

    df = get_btc_data_extended(days_back=180)
    df = build_feature_dataframe(df)
    df = df.dropna().reset_index(drop=True)

    balance = starting_balance
    position = None  # None = not holding BTC, otherwise the entry price

    for _, row in df.iterrows():
        if position is None and strategy["buy_rule"](row):
            position = row["close"]  # "buy" — remember entry price
        elif position is not None and strategy["sell_rule"](row):
            exit_price = row["close"]
            pct_change = (exit_price - position) / position
            balance *= (1 + pct_change)
            position = None  # "sell" — close the position

    return {
        "strategy_id": strategy_id,
        "starting_balance": starting_balance,
        "ending_balance": round(balance, 2),
        "total_return_pct": round((balance - starting_balance) / starting_balance * 100, 2),
    }


if __name__ == "__main__":
    result = run_backtest("rsi_oversold")
    print(result)