/**
 * Types mirroring docs/api-contract.md (contract version 1.0).
 *
 * Note: the contract itself flags Signal and BacktestResult field names as
 * "subject to change once ML confirms actual output shape." Keep usages of
 * these two types isolated behind services/apiClient.ts so a contract
 * change only requires updates here, not across every page.
 */

export interface Candle {
  timestamp: number; // unix epoch seconds
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface PricesResponse {
  symbol: string;
  interval: string;
  candles: Candle[];
}

export interface IndicatorPoint {
  timestamp: number; // unix epoch seconds
  rsi: number;
  macd: number;
  macd_signal: number;
  sma_20: number;
  sma_50: number;
}

export interface IndicatorsResponse {
  symbol: string;
  interval: string;
  indicators: IndicatorPoint[];
}

export interface Strategy {
  id: string;
  name: string;
  description: string;
  pros: string[];
  cons: string[];
}

export interface StrategiesResponse {
  strategies: Strategy[];
}

/** Shape flagged as unstable in the contract — confirm with ML before relying on exact fields. */
export interface Signal {
  symbol: string;
  signal: "BUY" | "HOLD" | "SELL";
  confidence: number;
  timestamp: number;
}

export interface Trade {
  entry_date: string; // ISO date
  exit_date: string; // ISO date
  entry_price: number;
  exit_price: number;
  return_pct: number;
}

/** Shape flagged as unstable in the contract — confirm with ML before relying on exact fields. */
export interface BacktestResult {
  strategy_id: string;
  start_date: string; // ISO date
  end_date: string; // ISO date
  total_return_pct: number;
  win_rate_pct: number;
  num_trades: number;
  trades: Trade[];
}

export interface UserStrategy {
  strategy_id: string | null;
  active: boolean;
  selected_at: string | null; // ISO datetime
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
  };
}
