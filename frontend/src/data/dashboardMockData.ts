import type { Signal } from "../types/api";
import type {
  MarketSummary,
  IndicatorSummaryItem,
  MarketStatus,
  ChartPoint,
} from "../types/dashboard";

/**
 * All Task 2 dashboard data lives here as mock/static values. When the real
 * backend (docs/api-contract.md) and ML model are ready, this file is the
 * only place that needs to be swapped for real fetched data — components
 * consume these values as props and don't know or care where they came from.
 */

const MOCK_TIMESTAMP = Math.floor(
  new Date("2026-09-10T10:30:00Z").getTime() / 1000
);

export const mockMarketSummary: MarketSummary = {
  symbol: "BTC",
  price: 67842.35,
  changePercent24h: 2.45,
  high24h: 68500.0,
  low24h: 65920.0,
  volume24h: 28_400_000_000,
};

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

export const mockChartData: ChartPoint[] = generateMockChartData();

/** 24 hourly mock candles with a gentle pseudo-random walk so the line looks like a real price chart. */
function generateMockChartData(): ChartPoint[] {
  const points: ChartPoint[] = [];
  const hourSeconds = 60 * 60;
  let price = 65500;

  for (let i = 23; i >= 0; i--) {
    const drift = Math.sin(i / 3) * 400 + (i % 5 === 0 ? 250 : -120);
    price = Math.max(64000, price + drift);
    points.push({
      timestamp: MOCK_TIMESTAMP - i * hourSeconds,
      close: Math.round(price * 100) / 100,
    });
  }

  return points;
}
