import type { MarketSummary } from "../../types/dashboard";
import "./MarketSummaryCard.css";

interface MarketSummaryCardProps {
  data: MarketSummary;
}

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

function formatVolume(volume: number): string {
  if (volume >= 1_000_000_000) {
    return `$${(volume / 1_000_000_000).toFixed(1)}B`;
  }
  if (volume >= 1_000_000) {
    return `$${(volume / 1_000_000).toFixed(1)}M`;
  }
  return currencyFormatter.format(volume);
}

export function MarketSummaryCard({ data }: MarketSummaryCardProps) {
  const isPositive = data.changePercent24h >= 0;

  return (
    <div className="market-summary-card">
      <span className="market-summary-title">Bitcoin ({data.symbol})</span>

      <div className="market-summary-grid">
        <div className="market-summary-stat">
          <span className="market-summary-label">Current Price</span>
          <span className="market-summary-value market-summary-price">
            {currencyFormatter.format(data.price)}
          </span>
        </div>

        <div className="market-summary-stat">
          <span className="market-summary-label">24h Change</span>
          <span
            className={`market-summary-value ${
              isPositive ? "market-summary-positive" : "market-summary-negative"
            }`}
          >
            {isPositive ? "+" : ""}
            {data.changePercent24h.toFixed(2)}%
          </span>
        </div>

        <div className="market-summary-stat">
          <span className="market-summary-label">24h High</span>
          <span className="market-summary-value">
            {currencyFormatter.format(data.high24h)}
          </span>
        </div>

        <div className="market-summary-stat">
          <span className="market-summary-label">24h Low</span>
          <span className="market-summary-value">
            {currencyFormatter.format(data.low24h)}
          </span>
        </div>

        <div className="market-summary-stat">
          <span className="market-summary-label">Volume</span>
          <span className="market-summary-value">
            {formatVolume(data.volume24h)}
          </span>
        </div>
      </div>
    </div>
  );
}
