import type { Signal } from "../types/api";
import type { IndicatorSummaryItem, MarketStatus } from "../types/dashboard";

/**
 * Remaining Task 3 mock data: signal, indicators, and market status stay
 * mock per Task 3 scope (Step 12) — only BTC price/chart data was replaced
 * with real API data (see services/priceService.ts). This file is still
 * the single place to swap these for real data in a future task.
 */

const MOCK_TIMESTAMP = Math.floor(
  new Date("2026-09-10T10:30:00Z").getTime() / 1000
);

// confidence is assumed to be a 0–1 fraction (displayed as a rounded
// percentage) since docs/api-contract.md does not yet specify the unit —
// flagged in types/api.ts as a field subject to change.
export const mockSignal: Signal = {
  symbol: "BTC",
  signal: "BUY",
  confidence: 0.82,
  timestamp: MOCK_TIMESTAMP,
};

export const mockIndicators: IndicatorSummaryItem[] = [
  { label: "RSI", value: "58.4", description: "Neutral" },
  { label: "MACD", value: "+125.6", description: "Bullish" },
  { label: "SMA 20", value: "$66,920", description: "Below Price" },
];

export const mockMarketStatus: MarketStatus = {
  pair: "BTC/USD",
  status: "Active",
  lastUpdated: "2026-09-10T10:30:00Z",
};
