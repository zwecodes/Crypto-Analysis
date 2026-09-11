import type { IndicatorSummaryItem } from "../../types/dashboard";
import "./DashboardCard.css";
import "./IndicatorCard.css";

interface IndicatorCardProps {
  item: IndicatorSummaryItem;
}

/**
 * Displays one indicator's latest mock value + a short label (e.g.
 * "Neutral", "Bullish"). Real indicator calculations (RSI/MACD/SMA) are
 * explicitly out of scope for Task 2 — this only renders whatever
 * IndicatorSummaryItem it's given.
 */
export function IndicatorCard({ item }: IndicatorCardProps) {
  return (
    <div className="dashboard-card indicator-card">
      <span className="dashboard-card-title">{item.label}</span>
      <span className="dashboard-card-value indicator-value">{item.value}</span>
      <span className="indicator-description">{item.description}</span>
    </div>
  );
}