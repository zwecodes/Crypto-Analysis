import { apiRequest } from "./apiClient";
import type { Candle, PricesResponse } from "../types/api";
import type { MarketSummary } from "../types/dashboard";

const SYMBOL = "BTC";
const DEFAULT_INTERVAL = "1h";
/** ~24h of hourly candles, matching the example query in docs/api-contract.md. */
const DEFAULT_LIMIT = 25;

interface GetBtcPricesOptions {
  interval?: string;
  limit?: number;
  offset?: number;
}

/**
 * Fetches BTC OHLCV candles from the existing GET /api/prices/btc endpoint.
 * This is a public market-data endpoint (no auth required), so requiresAuth
 * is set to false. The backend returns candles descending by timestamp —
 * this function sorts them ascending (oldest → newest) before returning,
 * since both the chart and the 24h stats below assume that order.
 */
export async function getBtcPrices(
  options: GetBtcPricesOptions = {}
): Promise<Candle[]> {
  const {
    interval = DEFAULT_INTERVAL,
    limit = DEFAULT_LIMIT,
    offset = 0,
  } = options;

  const params = new URLSearchParams({
    interval,
    limit: String(limit),
    offset: String(offset),
  });

  const response = await apiRequest<PricesResponse>(
    `/api/prices/btc?${params.toString()}`,
    { requiresAuth: false }
  );

  return [...response.candles].sort((a, b) => a.timestamp - b.timestamp);
}

/**
 * Derives dashboard market-summary stats from a window of ascending-order
 * candles (oldest first, newest last). Returns null for an empty window
 * rather than fabricating zeros, so the caller can show an explicit
 * "no data" state instead of a misleading $0.00 price.
 */
export function deriveMarketSummary(candles: Candle[]): MarketSummary | null {
  if (candles.length === 0) {
    return null;
  }

  const latest = candles[candles.length - 1];
  const oldest = candles[0];

  const high24h = Math.max(...candles.map((c) => c.high));
  const low24h = Math.min(...candles.map((c) => c.low));
  const volume24h = candles.reduce((sum, c) => sum + c.volume, 0);

  // Guard against a division-by-zero producing Infinity/NaN if the oldest
  // candle's close were ever 0 — never display a broken value regardless.
  const changePercent24h =
    oldest.close > 0
      ? ((latest.close - oldest.close) / oldest.close) * 100
      : 0;

  return {
    symbol: SYMBOL,
    price: latest.close,
    changePercent24h,
    high24h,
    low24h,
    volume24h,
  };
}