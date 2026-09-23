"""
Core backtesting engine — simulates a strategy's buy/sell rules
against historical data, logs individual trades, and computes summary stats.
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
    position = None  # None = not holding BTC, otherwise dict with entry info
    trades = []

    for _, row in df.iterrows():
        if position is None and strategy["buy_rule"](row):
            position = {"entry_date": row["open_time"], "entry_price": row["close"]}
        elif position is not None and strategy["sell_rule"](row):
            exit_price = row["close"]
            pct_change = (exit_price - position["entry_price"]) / position["entry_price"]
            balance *= (1 + pct_change)

            trades.append({
                "entry_date": str(position["entry_date"]),
                "exit_date": str(row["open_time"]),
                "entry_price": round(position["entry_price"], 2),
                "exit_price": round(exit_price, 2),
                "return_pct": round(pct_change * 100, 2),
            })
            position = None

    num_trades = len(trades)
    winning_trades = [t for t in trades if t["return_pct"] > 0]
    win_rate = round(len(winning_trades) / num_trades * 100, 2) if num_trades > 0 else 0.0

    return {
        "strategy_id": strategy_id,
        "starting_balance": starting_balance,
        "ending_balance": round(balance, 2),
        "total_return_pct": round((balance - starting_balance) / starting_balance * 100, 2),
        "num_trades": num_trades,
        "win_rate_pct": win_rate,
        "trades": trades,
    }


if __name__ == "__main__":
    result = run_backtest("rsi_oversold")
    print(f"Strategy: {result['strategy_id']}")
    print(f"Total return: {result['total_return_pct']}%")
    print(f"Num trades: {result['num_trades']}")
    print(f"Win rate: {result['win_rate_pct']}%")
    print(f"\nFirst 5 trades:")
    for t in result["trades"][:5]:
        print(t)