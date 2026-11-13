
import { useEffect, useState } from "react";
import { MarketSummaryCard } from "../../components/dashboard/MarketSummaryCard";
import { BtcPriceChart } from "../../components/dashboard/BtcPriceChart";
import { SignalCard } from "../../components/dashboard/SignalCard";
import { IndicatorCard } from "../../components/dashboard/IndicatorCard";
import { MarketStatusCard } from "../../components/dashboard/MarketStatusCard";
import { Spinner } from "../../components/ui/Spinner";
import { ErrorMessage } from "../../components/ui/ErrorMessage";
import { getBtcPrices, deriveMarketSummary } from "../../services/priceService";
import { getBtcIndicators } from "../../services/indicatorService";
import { getBtcSignal } from "../../services/signalService";
import type {
  MarketSummary,
  ChartPoint,
  IndicatorSummaryItem,
  MarketStatus,
} from "../../types/dashboard";
import type { IndicatorPoint, Signal } from "../../types/api";
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

type IndicatorState =
  | { status: "loading" }
  | { status: "error" }
  | { status: "empty" }
  | { status: "ready"; items: IndicatorSummaryItem[] };

type SignalState =
  | { status: "loading" }
  | { status: "error" }
  | { status: "empty" }
  | { status: "ready"; signal: Signal };

function formatIndicatorValue(value: number | null, prefix = ""): string {
  if (value === null || !Number.isFinite(value)) {
    return "N/A";
  }

  return `${prefix}${value.toLocaleString(undefined, {
    maximumFractionDigits: 2,
  })}`;
}

function describeRsi(value: number | null): string {
  if (value === null) return "Unavailable";
  if (value >= 70) return "Overbought";
  if (value <= 30) return "Oversold";
  return "Neutral";
}

function describeMacd(point: IndicatorPoint): string {
  if (point.macd === null || point.macd_signal === null) {
    return "Unavailable";
  }

  return point.macd >= point.macd_signal ? "Bullish" : "Bearish";
}

function buildIndicatorItems(point: IndicatorPoint): IndicatorSummaryItem[] {
  return [
    {
      label: "RSI",
      value: formatIndicatorValue(point.rsi),
      description: describeRsi(point.rsi),
    },
    {
      label: "MACD",
      value: formatIndicatorValue(point.macd),
      description: describeMacd(point),
    },
    {
      label: "MACD Signal",
      value: formatIndicatorValue(point.macd_signal),
      description: "Signal line",
    },
    {
      label: "SMA 20",
      value: formatIndicatorValue(point.sma_20, "$"),
      description: "20-period average",
    },
    {
      label: "SMA 50",
      value: formatIndicatorValue(point.sma_50, "$"),
      description: "50-period average",
    },
  ];
}

export function DashboardPage() {
  const [priceState, setPriceState] = useState<PriceState>({
    status: "loading",
  });

  const [indicatorState, setIndicatorState] = useState<IndicatorState>({
    status: "loading",
  });

  const [signalState, setSignalState] = useState<SignalState>({
    status: "loading",
  });

  const marketStatus: MarketStatus = {
    pair: "BTC/USD",
    status: priceState.status === "ready" ? "Connected" : "Unavailable",
    lastUpdated:
      priceState.status === "ready" ? priceState.lastUpdated : null,
  };

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
        console.error("Failed to load BTC prices:", error);
        setPriceState({ status: "error" });
      }
    }

    loadPrices();

    return () => {
      cancelled = true;
    };
  }, [retryCount]);

  useEffect(() => {
    let cancelled = false;

    async function loadIndicators() {
      setIndicatorState({ status: "loading" });

      try {
        const response = await getBtcIndicators({
          interval: "1h",
          limit: 200,
        });

        if (cancelled) return;

        const latest = response.indicators[0];

        if (!latest) {
          setIndicatorState({ status: "empty" });
          return;
        }

        setIndicatorState({
          status: "ready",
          items: buildIndicatorItems(latest),
        });
      } catch (error) {
        if (cancelled) return;
        console.error("Failed to load BTC indicators:", error);
        setIndicatorState({ status: "error" });
      }
    }

    loadIndicators();

    return () => {
      cancelled = true;
    };
  }, [retryCount]);

  useEffect(() => {
    let cancelled = false;

    async function loadSignal() {
      setSignalState({ status: "loading" });

      try {
        const response = await getBtcSignal();

        if (cancelled) return;

        // The backend returns a HOLD with null timestamp
        // when no ML prediction is available.
        if (response.timestamp === null) {
          setSignalState({ status: "empty" });
          return;
        }

        setSignalState({
          status: "ready",
          signal: response,
        });
      } catch (error) {
        if (cancelled) return;
        console.error("Failed to load BTC signal:", error);
        setSignalState({ status: "error" });
      }
    }

    loadSignal();

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
        <span className="dashboard-section-label-text">
          Technical Indicators (BTC · 1h)
        </span>
      </div>

      {indicatorState.status === "loading" && (
        <Spinner label="Loading technical indicators..." />
      )}

      {indicatorState.status === "error" && (
        <ErrorMessage
          message="Unable to load technical indicators. Please try again."
          onRetry={handleRetry}
        />
      )}

      {indicatorState.status === "empty" && (
        <ErrorMessage message="No technical indicator data is currently available." />
      )}

      {indicatorState.status === "ready" && (
        <div className="dashboard-grid">
          {indicatorState.items.map((item) => (
            <IndicatorCard key={item.label} item={item} />
          ))}
        </div>
      )}

      <div className="dashboard-section-label">
        <span className="dashboard-section-label-text">
          ML Trading Signal & Market Status
        </span>
      </div>

      {signalState.status === "loading" && (
        <Spinner label="Loading ML trading signal..." />
      )}

      {signalState.status === "error" && (
        <ErrorMessage
          message="Unable to load the ML trading signal. Please try again."
          onRetry={handleRetry}
        />
      )}

      {signalState.status === "empty" && (
        <p>No ML trading signal is currently available.</p>
      )}

      <div className="dashboard-grid">
        {signalState.status === "ready" && (
          <SignalCard signal={signalState.signal} />
        )}

        <MarketStatusCard status={marketStatus} />
      </div>
    </div>
  );
}
