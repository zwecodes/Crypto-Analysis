# API Contract

**Contract version: 1.1**

Base URL (dev): `http://localhost:8001`
Base URL (prod): `https://crypto-analysis-x1y8.onrender.com`

All authenticated endpoints require an `Authorization: Bearer <supabase_jwt>` header (from Supabase Auth on the frontend). Backend validates the JWT using the `supabase-py` client library (do not hand-roll JWT decoding).

If a breaking change is made to this contract, update this file first and announce it in `#general` before implementing.

### Changelog

- **1.1** — Backtest endpoint now returns a result only for an exact `start_date`/`end_date` match; a new `404 NO_MATCHING_BACKTEST` error replaces silently returning a different range. Documented dev port 8001, prod URL, health endpoints, caching, rate limiting, signals empty state, and the full error code list.
- **1.0** — Initial contract.

---

## Service endpoints

### GET /  and  GET /health
Lightweight liveness checks. Not rate limited. Keep-alive workflows ping `/health`.

Note: the production service runs on the Render free tier and sleeps after about 15 idle minutes. The first request after a sleep can take about a minute and may return an HTML splash page instead of JSON until the process is up.

---

## Auth

Handled directly by Supabase Auth on the frontend (sign up, login, session management) — no custom backend endpoints needed. Backend validates the JWT on protected routes using `supabase-py`.

---

## Prices

### GET /api/prices/btc
Returns recent BTC price history (OHLCV candles). Cached for 60 seconds.

**Query params:**
- `interval` (string, optional, default `"1h"`) — e.g. `1m`, `5m`, `1h`, `1d`
- `limit` (int, optional, default `200`)
- `offset` (int, optional, default `0`)

**Response 200:**
```json
{
  "symbol": "BTC",
  "interval": "1h",
  "candles": [
    {
      "timestamp": 1756339200,
      "open": 64000.5,
      "high": 65200.0,
      "low": 63800.0,
      "close": 65000.0,
      "volume": 1200.45
    }
  ]
}
```

---

## Indicators

### GET /api/indicators/btc
Returns computed technical indicators for BTC over a time range. Cached for 60 seconds. Indicator rows are written by the ML side; this endpoint only reads them.

**Query params:**
- `interval` (string, optional, default `"1h"`)
- `limit` (int, optional, default `200`)
- `offset` (int, optional, default `0`)

**Response 200:**
```json
{
  "symbol": "BTC",
  "interval": "1h",
  "indicators": [
    {
      "timestamp": 1756339200,
      "rsi": 42.3,
      "macd": 120.5,
      "macd_signal": 110.2,
      "sma_20": 64500.0,
      "sma_50": 63200.0
    }
  ]
}
```

---

## Strategies

Predefined strategies with AI-generated pros/cons. Pros/cons are generated **once** via an internal script (run by the ML team) and stored in the database — not generated live on request.

The only valid strategy ids are: `rsi_oversold`, `ma_crossover`, `macd_momentum`, `bollinger_bounce`, `ml_signal`.

### GET /api/strategies
Returns the list of predefined strategies. `pros` and `cons` are arrays of strings and may be empty.

**Response 200:**
```json
{
  "strategies": [
    {
      "id": "rsi_oversold",
      "name": "RSI Oversold/Overbought",
      "description": "Buys when RSI < 30, sells when RSI > 70",
      "pros": ["Simple to understand", "Works well in ranging markets"],
      "cons": ["Can give false signals in strong trends"]
    }
  ]
}
```

---

## Signals

### GET /api/signals/btc
Returns the current ML-generated BUY/HOLD/SELL signal.

**Response 200:**
```json
{
  "symbol": "BTC",
  "signal": "BUY",
  "confidence": 0.78,
  "timestamp": 1756339200
}
```

**Empty state:** if no signal has been written yet, the endpoint still returns 200 with `"signal": "HOLD"` and `"confidence": null`. Frontend must handle a null `confidence`.

*Note: field names subject to change once ML confirms actual model output shape — flag any needed changes here before frontend builds heavily against this.*

---

## Backtesting

### GET /api/backtest/{strategy_id}
Returns a stored backtest result for a strategy. The endpoint does **not** compute backtests; it reads results that the ML side has already written.

**Exact-range matching:** a result is returned only if its `start_date` and `end_date` match the requested range exactly. A different or partially overlapping range is never returned silently. If there is no exact match, the endpoint returns `404 NO_MATCHING_BACKTEST` (see below), and the message lists the available ranges.

**Path params:**
- `strategy_id` (string) — e.g. `rsi_oversold`

**Query params:**
- `start_date` (string, optional, ISO `YYYY-MM-DD`) — default: 182 days before `end_date`
- `end_date` (string, optional, ISO `YYYY-MM-DD`) — default: today (UTC)

Because of exact matching, the default range will usually not match a stored result. Clients should use a range that exists (see `Available ranges` in the 404 message) rather than relying on the defaults.

**Response 200:**
```json
{
  "strategy_id": "rsi_oversold",
  "start_date": "2026-03-31",
  "end_date": "2026-10-23",
  "total_return_pct": 12.4,
  "win_rate_pct": 58.0,
  "num_trades": 24,
  "trades": [
    {
      "entry_date": "2026-04-02",
      "exit_date": "2026-04-09",
      "entry_price": 62000.0,
      "exit_price": 64500.0,
      "return_pct": 4.03
    }
  ]
}
```
`total_return_pct` and `win_rate_pct` can be `null`. `trades` can be an empty array.

**Response 400 `BAD_REQUEST`:** `start_date` or `end_date` is not a valid ISO date, or `start_date` is after `end_date`.

**Response 404 `NOT_FOUND`:** the strategy id does not exist.
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Strategy 'xyz' not found"
  }
}
```

**Response 404 `NO_MATCHING_BACKTEST`:** the strategy exists but no stored result matches the requested range exactly. The message lists up to 3 available ranges (newest first), or says that no backtests have been computed yet.
```json
{
  "error": {
    "code": "NO_MATCHING_BACKTEST",
    "message": "No backtest result for 'rsi_oversold' from 2026-05-09 to 2026-11-09. Available ranges: 2026-03-31 to 2026-10-23."
  }
}
```

Frontend must tell these two 404s apart by `error.code`, not by HTTP status alone.

*Note: field names subject to change once ML confirms actual backtest output shape.*

---

## User Strategy Selection & Alerts (requires auth)

**Selecting a strategy = subscribing to email alerts for it.** There is no separate "view only" mode — picking a strategy on the dashboard automatically means the user will be emailed when its criteria are met.

Each user has at most one selection (one row per user). Selecting a new strategy replaces the previous one.

### GET /api/user/strategy
Returns the logged-in user's currently selected strategy (if any).

**Response 200:**
```json
{
  "strategy_id": "rsi_oversold",
  "active": true,
  "selected_at": "2026-08-20T10:00:00Z"
}
```
**Response 200 (none selected or deselected):**
```json
{
  "strategy_id": null,
  "active": false,
  "selected_at": null
}
```

### POST /api/user/strategy
Select (or switch to) a strategy. Automatically enables alerts for it (`active: true`).

**Request body:**
```json
{
  "strategy_id": "rsi_oversold"
}
```

**Response 200:**
```json
{
  "strategy_id": "rsi_oversold",
  "active": true,
  "selected_at": "2026-08-20T10:00:00Z"
}
```

### DELETE /api/user/strategy
Deselect the current strategy (turns off alerts, no strategy active). The stored row is kept and marked inactive.

**Response 204:** No content

---

## Rate limiting

All endpoints except `/` and `/health` are limited to 60 requests per minute per IP. Over the limit, the API returns `429` with error code `RATE_LIMITED`.

---

## Error format (all endpoints)

Every error response, including request validation errors, uses this shape (never FastAPI's default `{ "detail": ... }`):

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Strategy 'xyz' not found"
  }
}
```

| HTTP status | `error.code` | Meaning |
|---|---|---|
| 400 | `BAD_REQUEST` | Invalid or missing request input |
| 401 | `UNAUTHORIZED` | Missing, invalid, or expired JWT |
| 404 | `NOT_FOUND` | Resource (for example a strategy id) does not exist |
| 404 | `NO_MATCHING_BACKTEST` | Strategy exists, but no stored backtest for the exact date range |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Unexpected server error |

Clients should branch on `error.code`, not only on the HTTP status.

---

## Notes for implementers

- All timestamps are Unix epoch seconds (UTC) unless noted otherwise (dates in backtest use ISO format).
- All prices are in USD.
- This contract is the source of truth. Update here first, then implement.