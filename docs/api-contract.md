# API Contract

**Contract version: 1.0**

Base URL (dev): `http://localhost:8000`
Base URL (prod): TBD after deployment

All authenticated endpoints require an `Authorization: Bearer <supabase_jwt>` header (from Supabase Auth on the frontend). Backend validates the JWT using the `supabase-py` client library (do not hand-roll JWT decoding).

If a breaking change is made to this contract, update this file first and announce it in `#general` before implementing.

---

## Auth

Handled directly by Supabase Auth on the frontend (sign up, login, session management) — no custom backend endpoints needed. Backend validates the JWT on protected routes using `supabase-py`.

---

## Prices

### GET /api/prices/btc
Returns recent BTC price history (OHLCV candles).

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
Returns computed technical indicators for BTC over a time range.

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

### GET /api/strategies
Returns the list of predefined strategies.

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
*Note: field names subject to change once ML confirms actual model output shape — flag any needed changes here before frontend builds heavily against this.*

---

## Backtesting

### GET /api/backtest/{strategy_id}
Returns historical backtest results for a given strategy.

**Path params:**
- `strategy_id` (string) — e.g. `rsi_oversold`

**Query params:**
- `start_date` (string, optional, ISO format) — default: 6 months ago
- `end_date` (string, optional, ISO format) — default: now

**Response 200:**
```json
{
  "strategy_id": "rsi_oversold",
  "start_date": "2026-03-01",
  "end_date": "2026-08-31",
  "total_return_pct": 12.4,
  "win_rate_pct": 58.0,
  "num_trades": 24,
  "trades": [
    {
      "entry_date": "2026-03-15",
      "exit_date": "2026-03-22",
      "entry_price": 62000.0,
      "exit_price": 64500.0,
      "return_pct": 4.03
    }
  ]
}
```
*Note: field names subject to change once ML confirms actual backtest output shape.*

---

## User Strategy Selection & Alerts (requires auth)

**Selecting a strategy = subscribing to email alerts for it.** There is no separate "view only" mode — picking a strategy on the dashboard automatically means the user will be emailed when its criteria are met.

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
**Response 200 (none selected):**
```json
{
  "strategy_id": null,
  "active": false,
  "selected_at": null
}
```

### POST /api/user/strategy
Select (or switch to) a strategy. Automatically enables alerts for it, and deactivates any previous selection.

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
Deselect the current strategy (turns off alerts, no strategy active).

**Response 204:** No content

---

## Error format (all endpoints)

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Strategy 'xyz' not found"
  }
}
```

Standard HTTP status codes: `400` (bad request), `401` (unauthorized), `404` (not found), `500` (server error).

---

## Notes for implementers

- All timestamps are Unix epoch seconds (UTC) unless noted otherwise (dates in backtest use ISO format).
- All prices are in USD.
- This contract is the source of truth. Update here first, then implement.