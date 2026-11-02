"""Pure decision helpers for the alert job (no network, no database)."""
from datetime import datetime, timedelta, timezone

COOLDOWN_HOURS = 6


def parse_timestamp(value):
    """Turn a Supabase timestamp (string, datetime or None) into an aware datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def cooldown_passed(last_alerted_at, now, hours=COOLDOWN_HOURS):
    """True if the user was never alerted, or the last alert is old enough."""
    last = parse_timestamp(last_alerted_at)
    if last is None:
        return True
    return now - last >= timedelta(hours=hours)


def ml_signal_change(latest_signal, previous_signal):
    """Return BUY or SELL only when the model signal changed to BUY or SELL. Never on HOLD."""
    if latest_signal in ("BUY", "SELL") and latest_signal != previous_signal:
        return latest_signal
    return None