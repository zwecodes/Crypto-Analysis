-- =========================================
-- PRICES TABLE
-- Stores BTC OHLCV candle data
-- =========================================
CREATE TABLE prices (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL DEFAULT 'BTC',
    interval TEXT NOT NULL,        -- e.g. '1h', '1d'
    timestamp BIGINT NOT NULL,     -- unix epoch seconds
    open NUMERIC NOT NULL,
    high NUMERIC NOT NULL,
    low NUMERIC NOT NULL,
    close NUMERIC NOT NULL,
    volume NUMERIC NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (symbol, interval, timestamp)
);

CREATE INDEX idx_prices_symbol_interval_timestamp 
    ON prices (symbol, interval, timestamp DESC);

-- =========================================
-- INDICATORS TABLE
-- Stores computed technical indicators per candle
-- =========================================
CREATE TABLE indicators (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL DEFAULT 'BTC',
    interval TEXT NOT NULL,
    timestamp BIGINT NOT NULL,
    rsi NUMERIC,
    macd NUMERIC,
    macd_signal NUMERIC,
    sma_20 NUMERIC,
    sma_50 NUMERIC,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (symbol, interval, timestamp)
);

CREATE INDEX idx_indicators_symbol_interval_timestamp 
    ON indicators (symbol, interval, timestamp DESC);

-- =========================================
-- STRATEGIES TABLE
-- Predefined strategies with AI-generated pros/cons
-- =========================================
CREATE TABLE strategies (
    id TEXT PRIMARY KEY,           -- e.g. 'rsi_oversold'
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    pros JSONB NOT NULL DEFAULT '[]',   -- array of strings
    cons JSONB NOT NULL DEFAULT '[]',   -- array of strings
    created_at TIMESTAMPTZ DEFAULT now()
);

-- =========================================
-- SIGNALS TABLE
-- ML-generated BUY/HOLD/SELL signals over time
-- =========================================
CREATE TABLE signals (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL DEFAULT 'BTC',
    signal TEXT NOT NULL CHECK (signal IN ('BUY', 'HOLD', 'SELL')),
    confidence NUMERIC,
    timestamp BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (symbol, timestamp)
);

CREATE INDEX idx_signals_symbol_timestamp 
    ON signals (symbol, timestamp DESC);

-- =========================================
-- USER_STRATEGY TABLE
-- Links a user to their currently selected strategy 
-- (selection = alert subscription, per Option A)
-- =========================================
CREATE TABLE user_strategy (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    strategy_id TEXT NOT NULL REFERENCES strategies(id),
    active BOOLEAN NOT NULL DEFAULT true,
    selected_at TIMESTAMPTZ DEFAULT now(),
    last_alerted_at TIMESTAMPTZ,   -- used for alert cooldown logic
    UNIQUE (user_id)  -- one active strategy per user at a time
);

CREATE INDEX idx_user_strategy_user_id ON user_strategy (user_id);

-- =========================================
-- BACKTEST_RESULTS TABLE (cached results, optional but recommended)
-- Avoids recomputing backtests on every request
-- =========================================
CREATE TABLE backtest_results (
    id BIGSERIAL PRIMARY KEY,
    strategy_id TEXT NOT NULL REFERENCES strategies(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_return_pct NUMERIC,
    win_rate_pct NUMERIC,
    num_trades INT,
    trades JSONB,   -- array of trade objects
    computed_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (strategy_id, start_date, end_date)
);

-- =========================================
-- ROW LEVEL SECURITY (RLS)
-- =========================================

-- Public read-only tables: prices, indicators, strategies, signals, backtest_results
ALTER TABLE prices ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read access" ON prices FOR SELECT USING (true);

ALTER TABLE indicators ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read access" ON indicators FOR SELECT USING (true);

ALTER TABLE strategies ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read access" ON strategies FOR SELECT USING (true);

ALTER TABLE signals ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read access" ON signals FOR SELECT USING (true);

ALTER TABLE backtest_results ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read access" ON backtest_results FOR SELECT USING (true);

-- user_strategy: users can only see/edit their OWN row
ALTER TABLE user_strategy ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own strategy" 
    ON user_strategy FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own strategy" 
    ON user_strategy FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own strategy" 
    ON user_strategy FOR UPDATE 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own strategy" 
    ON user_strategy FOR DELETE 
    USING (auth.uid() = user_id);