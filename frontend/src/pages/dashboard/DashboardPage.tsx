import { useEffect, useState } from "react";
import { MarketSummaryCard } from "../../components/dashboard/MarketSummaryCard";
import { BtcPriceChart } from "../../components/dashboard/BtcPriceChart";
import { SignalCard } from "../../components/dashboard/SignalCard";
import { IndicatorCard } from "../../components/dashboard/IndicatorCard";
import { MarketStatusCard } from "../../components/dashboard/MarketStatusCard";
import { Spinner } from "../../components/ui/Spinner";
import { ErrorMessage } from "../../components/ui/ErrorMessage";
import { getBtcPrices, deriveMarketSummary } from "../../services/priceService";
import {
  mockSignal,
  mockIndicators,
  mockMarketStatus,
} from "../../data/dashboardMockData";
import type { MarketSummary, ChartPoint } from "../../types/dashboard";
import "./DashboardPage.css";

type PriceState =
  | { status: "loading" }
  | { status: "error" }
  | { status: "empty" }
  | {
      status: "ready";
      summary: MarketSummary;
      chartData: ChartPoint[];
      lastUpdated: string;
    };

/**
 * Task 3 scope: BTC price summary + chart now come from the real backend
 * (services/priceService.ts -> GET /api/prices/btc). Signal, indicators,
 * and market status remain mock data per Task 3's explicit scope limit —
 * those stay untouched from data/dashboardMockData.ts.
 */
export function DashboardPage() {
  const [priceState, setPriceState] = useState<PriceState>({ status: "loading" });
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function loadPrices() {
      setPriceState({ status: "loading" });
      try {
        const candles = await getBtcPrices();
        if (cancelled) return;

        const summary = deriveMarketSummary(candles);
        if (!summary) {
          setPriceState({ status: "empty" });
          return;
        }

        const chartData: ChartPoint[] = candles.map((c) => ({
          timestamp: c.timestamp,
          close: c.close,
        }));

        setPriceState({
          status: "ready",
          summary,
          chartData,
          lastUpdated: new Date(
            candles[candles.length - 1].timestamp * 1000
          ).toLocaleString(),
        });
      } catch (error) {
        if (cancelled) return;
        // Never surface the raw backend/Supabase error message to the user.
        console.error("Failed to load BTC prices:", error);
        setPriceState({ status: "error" });
      }
    }

    loadPrices();

    return () => {
      cancelled = true;
    };
  }, [retryCount]);

  function handleRetry() {
    setRetryCount((count) => count + 1);
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-page-header">
        <div>
          <h1>Dashboard</h1>
          <p className="dashboard-page-subtitle">Bitcoin market overview</p>
        </div>
      </div>

      {priceState.status === "loading" && (
        <Spinner label="Loading BTC market data..." />
      )}

      {priceState.status === "error" && (
        <ErrorMessage
          message="Unable to load BTC market data. Please try again."
          onRetry={handleRetry}
        />
      )}

      {priceState.status === "empty" && (
        <ErrorMessage message="No BTC market data is currently available." />
      )}

      {priceState.status === "ready" && (
        <>
          <MarketSummaryCard
            data={priceState.summary}
            lastUpdated={priceState.lastUpdated}
          />
          <BtcPriceChart data={priceState.chartData} />
        </>
      )}

      <div className="dashboard-section-label">
        <span className="dashboard-demo-badge">Mock data</span>
        <span className="dashboard-section-label-text">
          Signal &amp; indicators shown below are for demonstration only
        </span>
      </div>

      <div className="dashboard-grid">
        <SignalCard signal={mockSignal} />
        {mockIndicators.map((item) => (
          <IndicatorCard key={item.label} item={item} />
        ))}
        <MarketStatusCard status={mockMarketStatus} />
      </div>
    </div>
  );
}
