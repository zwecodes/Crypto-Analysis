# Integration testing report (#74 and #77)

Date: 2026-11-24 (UTC). Tester: Zwe.

## Environment

- Frontend: https://crypto-analysis-ten.vercel.app (Vercel, Root Directory `frontend`, connected to the GitHub repo, includes the `frontend/vercel.json` single-page-app rewrite)
- Backend: https://crypto-analysis-x1y8.onrender.com (Render free tier)
- API contract: `docs/api-contract.md` v1.2
- Auth and database: Supabase (Site URL and Redirect URLs point to `https://crypto-analysis-ten.vercel.app`)

## Summary

The integration pass is **passed with known limitations** (section 4). Still open before the **2026-11-27** submission: confirming the first live alert email delivery when a signal transitions in `LIVE` mode (section 5).

## 1. Backend contract checks (#74)

| Check | Result | Tested on |
|---|---|---|
| `GET /api/signals/btc` | 200, `HOLD`, confidence 0.79, timestamp 2026-11-20 05:00 UTC | production |
| `GET /api/user/strategy` without a token | 401 `UNAUTHORIZED`, contract error shape | production |
| `GET /api/backtest/rsi_oversold?start_date=bad&end_date=2026-11-18` | 400 `BAD_REQUEST`, "start_date must be an ISO date" | production |
| `GET /api/backtest/rsi_oversold/ranges` | 200, `start_date` 2026-03-31, `min_end_date` 2026-04-30, `max_end_date` 2026-11-18 | production (2026-11-19) |
| `GET /api/backtest/{id}` with a stored range | 200 with total return, win rate, trade count and trades (RSI: 22.53%, 72.86%, 70 trades) | production, via the Backtest page |
| Backtest range with no stored result | 404 `NO_MATCHING_BACKTEST`, message lists available ranges | local, `main` |
| `/ranges` for `ml_signal` and for an unknown strategy | 404 `NO_MATCHING_BACKTEST` and 404 `NOT_FOUND` | local, `main` |
| `GET /api/prices/btc`, `/api/indicators/btc`, `/api/strategies` | 200, used by the live dashboard and Strategy Picker | production |
| Select and turn off a strategy (`/api/user/strategy`) | Selecting enables alerts, "Turn off alerts" disables them | production, via the UI |
| Rate limit (`429 RATE_LIMITED`, >60 req/min) | 429 triggered after 60 requests in 34.33s (production sequential `curl` took 97.77s for 70 requests, staying below 60 req/min) | local (and timed on production) |
| Automated backend tests | 29 passed (`pytest` in `backend/`) | local |

## 2. Frontend flows on the live site (#77)

| Flow | Result |
|---|---|
| Login, logout, login again | Pass |
| Open `/dashboard` and `/backtest` directly and refresh | Pass (no 404) |
| Dashboard | Pass: price, 24h change/high/low/volume, 24h chart, RSI 34.47, MACD -430.6, MACD signal -346.19, SMA 20 $62,913.32, SMA 50 $63,347.02, signal HOLD 79%, market status Connected |
| Strategy Picker | Pass: five strategies with regenerated pros/cons (RSI Oversold reflects 71 trades, 71.8% win rate, 5.69% return; leftover `test_strategy` row removed), MACD Momentum selected with alerts enabled |
| Backtest Results | Pass: start date 2026-03-31, end date defaults to the newest (2026-11-18), result and trade history table shown; `ml_signal` displays `"No backtest results have been computed for this strategy yet."` (resolved loading spinner issue) |
| Alert Settings | Pass: MACD Momentum, Active, subscription start time shown |
| Alert email | Pass: the `[TEST]` alert arrived in the Primary inbox |

## 3. Data pipelines

| Data | Schedule | Status |
|---|---|---|
| Prices | Hourly (GitHub Actions) | Working. Binance is reached through `data-api.binance.vision` since PR #101 (the original error was HTTP 451 from GitHub's US runners). Observed about 3 hours behind on the dashboard at 06:31 UTC. |
| Indicators | Hourly, in the same workflow (Python 3.12) | Working, values shown on the dashboard |
| Signals | Hourly, inside Kaung's alert job (reads candles from Binance directly) | Working, fresh timestamp |
| Backtests | Daily, 00:45 UTC | Working. Newest end date is yesterday (UTC), one stored result per strategy per closed day from 2026-03-31. `ml_signal` has none (intentional). |

## 4. Known limitations & minor issues

1. GitHub scheduled workflows are best-effort. Runs can be delayed by hours (about 7 to 9 hours between scheduled alert-job runs observed), so prices, indicators and alerts can lag.
2. Dashboard cards show different "as of" times: prices and indicators come from Supabase, while the signal is computed from Binance directly by the alert job.
3. The backtest counts closed trades only. Per Saw, RSI Oversold bought on Nov 8 at 21:00 and held through Nov 18 (unrealized loss excluded from `2026-11-15` and `2026-11-18` totals of 22.53%, 72.86%, 70 trades); once that Nov 8 position closed at a loss, the latest window updated to 71 trades and 5.69%. Saw will mention this limitation in the demo.
4. The pros/cons text quotes numbers from the backtest, which change. Saw regenerated them for all four strategies on 2026-11-20 using the latest window and plans to remove the numbers from the text after the demo.
5. `ml_signal` has no backtest and no pros/cons. This is intentional (the model is trained on the same period, so a backtest would be mostly in-sample, and the explainer builds from backtest numbers).
6. The Render free tier takes about a minute to wake up after idle time.

## 5. Not verified / open

- **Signals empty state** (`HOLD` with `null` confidence): not tested, because production has a real signal.
- **Real alert end to end** (a signal flips, the email is sent, `last_alerted_at` is saved, nothing repeats within 6 hours): go-live PR is merged and scheduled runs are confirmed active in `Mode: LIVE` (run `#28` logged `'users': 2, 'no_change': 2, 'sent': 0`); waiting for a live signal transition to trigger and verify.

## 6. Next steps and decisions

- **Submission / demo date:** `2026-11-27`.
- Scheduled alert-job runs are live in `Mode: LIVE` for any user with an active strategy (quick kill switch via `Actions → Alert job → ⋯ → Disable workflow`). Watching `zweaung1266@gmail.com` and `last_alerted_at` in Supabase for `sent: 1` on a real signal flip before closing `#49` and `#76`.
- After submission/demo: remove numbers from the pros/cons text.