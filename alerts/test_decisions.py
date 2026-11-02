from datetime import datetime, timedelta, timezone

from decisions import cooldown_passed, ml_signal_change, parse_timestamp

NOW = datetime(2026, 10, 24, 12, 0, tzinfo=timezone.utc)


def test_never_alerted_passes():
    assert cooldown_passed(None, NOW) is True


def test_recent_alert_blocks():
    assert cooldown_passed((NOW - timedelta(hours=3)).isoformat(), NOW) is False


def test_old_alert_passes():
    assert cooldown_passed((NOW - timedelta(hours=6)).isoformat(), NOW) is True
    assert cooldown_passed((NOW - timedelta(hours=7)).isoformat(), NOW) is True


def test_z_suffix_is_understood():
    assert parse_timestamp("2026-10-24T09:00:00Z") == NOW - timedelta(hours=3)


def test_ml_change_to_buy_or_sell():
    assert ml_signal_change("BUY", "HOLD") == "BUY"
    assert ml_signal_change("SELL", "BUY") == "SELL"
    assert ml_signal_change("BUY", None) == "BUY"


def test_ml_no_change_or_hold():
    assert ml_signal_change("BUY", "BUY") is None
    assert ml_signal_change("HOLD", "BUY") is None
    assert ml_signal_change(None, "BUY") is None