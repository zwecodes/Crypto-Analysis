"""
Dry run of the alert check: no database, no email.

Fetches 200 hourly candles, adds the indicator columns with Saw's
build_feature_dataframe, drops the still-open candle, and prints which
strategies would fire (change-only) on the latest closed candle.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "ml"))  # the ml modules use flat imports
sys.path.insert(0, HERE)

from criteria import check_signal  # noqa: E402
from data import get_btc_data  # noqa: E402
from features import build_feature_dataframe  # noqa: E402
from strategies import STRATEGIES  # noqa: E402

CANDLES = 200
HISTORY = 48


def closed_candles(count=CANDLES):
    df = get_btc_data(interval="1h", limit=count)
    df = build_feature_dataframe(df)
    return df.iloc[:-1].reset_index(drop=True)  # drop the still-open candle


def main():
    frame = closed_candles()
    previous, current = frame.iloc[-2], frame.iloc[-1]

    print(f"Closed candles used: {len(frame)}")
    print(f"Latest closed candle: {current['open_time']}")
    print(
        f"close={current['close']:.2f}  rsi={current['rsi']:.1f}  "
        f"ema_20={current['ema_20']:.1f}  sma_50={current['sma_50']:.1f}"
    )
    print()

    print("Would fire on the latest closed candle:")
    rule_strategies = []
    for strategy in STRATEGIES:
        if strategy.get("buy_criteria") is None and strategy.get("sell_criteria") is None:
            print(f"  {strategy['id']}: model-based, checked separately")
            continue
        rule_strategies.append(strategy)
        print(f"  {strategy['id']}: {check_signal(strategy, previous, current) or 'no change'}")

    print()
    print(f"Signals over the last {HISTORY} closed candles (to choose the cooldown):")
    for strategy in rule_strategies:
        fired = []
        for i in range(len(frame) - HISTORY, len(frame)):
            signal = check_signal(strategy, frame.iloc[i - 1], frame.iloc[i])
            if signal:
                fired.append(f"{frame.iloc[i]['open_time']:%m-%d %H:%M} {signal}")
        print(f"  {strategy['id']}: {len(fired)}")
        for line in fired:
            print(f"      {line}")


if __name__ == "__main__":
    main()