import type { Candle } from "./api";

/**
 * Dashboard-specific types. `Signal` and `Candle` from ./api are reused
 * as-is where the mock data matches a real future response shape exactly.
 * These types below have no backend-contract equivalent (yet) — they
 * represent UI-level summaries/derived values, not raw API responses.
 */

export interface MarketSummary {
  symbol: string;
  price: number;
  changePercent24h: number;
  high24h: number;
  low24h: number;
  volume24h: number;
}

/** A single indicator display card: a derived value + a short human label. */
export interface IndicatorSummaryItem {
  label: string;
  value: string;
  description: string;
}

export interface MarketStatus {
  pair: string;
  status: "Active" | "Inactive";
  lastUpdated: string; // ISO datetime string
}

/** Minimal shape the chart needs from a Candle — reused rather than duplicated. */
export type ChartPoint = Pick<Candle, "timestamp" | "close">;