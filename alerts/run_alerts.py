"""
Hourly alert job.

Reads active rows from user_strategy, decides who should be alerted
(change-only signal + 6 hour cooldown), and sends an email.

DRY_RUN is on unless DRY_RUN=false. In dry-run mode nothing is sent, no
user emails are fetched, and last_alerted_at is not changed.

Logs are public, so this script prints counts only: never user ids,
emails, keys or error messages.
"""
import os
import smtplib
import sys
from datetime import datetime, timezone
from email.message import EmailMessage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "ml"))  # the ml modules use flat imports
sys.path.insert(0, HERE)

from supabase import create_client  # noqa: E402

from criteria import check_signal  # noqa: E402
from decisions import cooldown_passed, ml_signal_change  # noqa: E402
from dry_run import closed_candles  # noqa: E402
from strategies import get_strategy  # noqa: E402

DRY_RUN = os.getenv("DRY_RUN", "true").strip().lower() != "false"


def get_client():
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SECRET_KEY", "")
    if not url or not key:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SECRET_KEY")
    url = url.removesuffix("/rest/v1/").removesuffix("/rest/v1")
    return create_client(url, key)


def latest_ml_signals(client):
    """Return (latest, previous) ml signal, or (None, None) if there is not enough history."""
    rows = (
        client.table("signals")
        .select("signal,timestamp")
        .eq("symbol", "BTC")
        .order("timestamp", desc=True)
        .limit(2)
        .execute()
        .data
    )
    if len(rows) < 2:
        return None, None
    return rows[0]["signal"], rows[1]["signal"]


def get_user_email(client, user_id):
    return client.auth.admin.get_user_by_id(user_id).user.email


def send_email(to_address, strategy_name, signal, price):
    msg = EmailMessage()
    msg["Subject"] = f"BTC {signal} alert: {strategy_name}"
    msg["From"] = os.environ["EMAIL_USER"]
    msg["To"] = to_address
    msg.set_content(
        f"Your strategy \"{strategy_name}\" just signalled {signal} on BTC.\n"
        f"Latest closed hourly candle: close = {price:,.2f} USD.\n\n"
        "This is an automated alert from the Crypto-Analysis project. "
        "It is not financial advice."
    )
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(os.environ["EMAIL_USER"], os.environ["EMAIL_APP_PASSWORD"])
        server.send_message(msg)


def main():
    print(f"Mode: {'DRY RUN (no emails)' if DRY_RUN else 'LIVE (emails will be sent)'}")
    client = get_client()
    now = datetime.now(timezone.utc)

    frame = closed_candles()
    previous, current = frame.iloc[-2], frame.iloc[-1]
    price = float(current["close"])
    ml_latest, ml_previous = latest_ml_signals(client)

    subscriptions = (
        client.table("user_strategy")
        .select("user_id,strategy_id,last_alerted_at")
        .eq("active", True)
        .execute()
        .data
    )

    counts = {"users": len(subscriptions), "no_change": 0, "cooldown": 0,
              "would_send": 0, "sent": 0, "failed": 0}

    for sub in subscriptions:
        strategy_id = sub["strategy_id"]
        if strategy_id == "ml_signal":
            signal = ml_signal_change(ml_latest, ml_previous) if ml_latest else None
        else:
            signal = check_signal(get_strategy(strategy_id), previous, current)

        if signal is None:
            counts["no_change"] += 1
            continue
        if not cooldown_passed(sub["last_alerted_at"], now):
            counts["cooldown"] += 1
            continue
        if DRY_RUN:
            counts["would_send"] += 1
            print(f"  would alert: {strategy_id} {signal}")
            continue

        try:
            email = get_user_email(client, sub["user_id"])
            send_email(email, get_strategy(strategy_id)["name"], signal, price)
            client.table("user_strategy").update(
                {"last_alerted_at": now.isoformat()}
            ).eq("user_id", sub["user_id"]).execute()
            counts["sent"] += 1
        except Exception as exc:
            counts["failed"] += 1
            print(f"  send failed for a {strategy_id} user: {type(exc).__name__}")

    print(f"Summary: {counts}")
    if counts["failed"]:
        sys.exit(1)  # make the Actions run show red


if __name__ == "__main__":
    main()