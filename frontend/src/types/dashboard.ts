import type { Candle } from "./api";

/**
 * Dashboard-specific types for UI-level summaries and derived values.
 * Candle is reused from the backend API types.
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
  status: "Connected" | "Unavailable";
  lastUpdated: string | null;
}

/** Minimal shape the chart needs from a Candle — reused rather than duplicated. */
export type ChartPoint = Pick<Candle, "timestamp" | "close">;