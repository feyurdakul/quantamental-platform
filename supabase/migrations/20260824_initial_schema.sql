-- ==============================================================================
-- Quantamental Platform — PostgreSQL / Supabase Veritabanı Şeması
-- sistem_mimari.md Spesifikasyonu Tam Uyumu (Bölüm 2, 3, 4, 8, 9)
-- ==============================================================================

-- 1. Varlık Evreni Tablosu (Bölüm 2 & 3.1)
CREATE TABLE IF NOT EXISTS assets (
    symbol VARCHAR(50) PRIMARY KEY,                    -- Kanonik sembol: 'BIST:THYAO', 'NASDAQ:AAPL'
    name VARCHAR(255) NOT NULL,                        -- Varlık adı
    asset_class VARCHAR(50) NOT NULL,                  -- BIST_STOCK, US_STOCK, BANK_STOCK, ETF, CRYPTO, FOREX, COMMODITY, INDEX
    exchange VARCHAR(50) NOT NULL,                     -- BIST, NASDAQ, NYSE, AMEX, BINANCE vb.
    sector VARCHAR(100),                               -- Sektör
    industry VARCHAR(100),                             -- Alt sektör
    currency VARCHAR(10) NOT NULL DEFAULT 'TRY',       -- Ana para birimi
    is_active BOOLEAN NOT NULL DEFAULT TRUE,           -- Aktif tarama listesinde mi?
    requires_financials BOOLEAN NOT NULL DEFAULT TRUE, -- Finansal tablo gerektirir mi?
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_assets_class ON assets(asset_class);
CREATE INDEX IF NOT EXISTS idx_assets_exchange ON assets(exchange);
CREATE INDEX IF NOT EXISTS idx_assets_active ON assets(is_active);

-- 2. Günlük Piyasa & OHLCV Veri Tablosu (Bölüm 3.2)
CREATE TABLE IF NOT EXISTS market_data_daily (
    symbol VARCHAR(50) NOT NULL REFERENCES assets(symbol) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,                    -- Mum tarihi (UTC)
    open NUMERIC(18, 6) NOT NULL,
    high NUMERIC(18, 6) NOT NULL,
    low NUMERIC(18, 6) NOT NULL,
    close NUMERIC(18, 6) NOT NULL,
    adjusted_close NUMERIC(18, 6),                     -- Bölünme/temettü düzeltmeli fiyat
    volume NUMERIC(24, 4),
    currency VARCHAR(10) NOT NULL DEFAULT 'TRY',
    source_name VARCHAR(50) NOT NULL,                  -- TradingView, yfinance, isyatirimhisse
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (symbol, timestamp)
);

CREATE INDEX IF NOT EXISTS idx_market_data_symbol_ts ON market_data_daily(symbol, timestamp DESC);

-- 3. Finansal Tablo Snapshot'ları Tablosu (Bölüm 3.3, 3.4 & 4.1)
CREATE TABLE IF NOT EXISTS financial_snapshots (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL REFERENCES assets(symbol) ON DELETE CASCADE,
    period_type VARCHAR(20) NOT NULL,                  -- annual, quarterly, ttm, mrq
    period_end DATE NOT NULL,                          -- Dönem bitiş tarihi (örn: 2024-12-31)
    as_of_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_name VARCHAR(50) NOT NULL,                  -- isyatirimhisse, FMP, yfinance, GoogleFinance
    source_endpoint VARCHAR(100),
    currency VARCHAR(10) NOT NULL DEFAULT 'TRY',
    formula_version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    status VARCHAR(30) NOT NULL DEFAULT 'valid',       -- valid, missing, invalid, insufficient_data, structural_na
    is_usd_converted BOOLEAN NOT NULL DEFAULT FALSE,   -- TMS-29 enflasyon arındırmalı USD bilanço mu?
    comparability_limited BOOLEAN NOT NULL DEFAULT FALSE,

    -- Gelir Tablosu (11 Kalem)
    revenue NUMERIC(24, 2),
    cost_of_revenue NUMERIC(24, 2),
    gross_profit NUMERIC(24, 2),
    operating_income NUMERIC(24, 2),
    ebitda NUMERIC(24, 2),
    interest_expense NUMERIC(24, 2),
    pretax_income NUMERIC(24, 2),
    income_tax_expense NUMERIC(24, 2),
    net_income NUMERIC(24, 2),
    eps_diluted NUMERIC(14, 4),
    weighted_average_shares_diluted NUMERIC(24, 2),

    -- Bilanço (13 Kalem)
    cash_and_short_term_investments NUMERIC(24, 2),
    accounts_receivable NUMERIC(24, 2),
    inventory NUMERIC(24, 2),
    total_current_assets NUMERIC(24, 2),
    total_assets NUMERIC(24, 2),
    short_term_debt NUMERIC(24, 2),
    long_term_debt NUMERIC(24, 2),
    total_debt NUMERIC(24, 2),
    accounts_payable NUMERIC(24, 2),
    total_current_liabilities NUMERIC(24, 2),
    total_liabilities NUMERIC(24, 2),
    total_stockholders_equity NUMERIC(24, 2),
    retained_earnings NUMERIC(24, 2),

    -- Nakit Akış Tablosu (6 Kalem)
    operating_cash_flow NUMERIC(24, 2),
    capital_expenditure NUMERIC(24, 2),
    free_cash_flow NUMERIC(24, 2),
    depreciation_and_amortization NUMERIC(24, 2),
    share_issuance_or_repurchase NUMERIC(24, 2),
    dividends_paid NUMERIC(24, 2),

    -- Piyasa Bağlamı (4 Kalem)
    market_cap NUMERIC(24, 2),
    enterprise_value NUMERIC(24, 2),
    shares_outstanding NUMERIC(24, 2),
    current_price NUMERIC(18, 4),

    raw_data JSONB,                                    -- Ham JSON yedeği
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_symbol_period UNIQUE (symbol, period_type, period_end, is_usd_converted)
);

CREATE INDEX IF NOT EXISTS idx_fin_snapshots_symbol_period ON financial_snapshots(symbol, period_end DESC);
CREATE INDEX IF NOT EXISTS idx_fin_snapshots_status ON financial_snapshots(status);

-- 4. Analist Tahminleri ve Sürprizler (Finnhub)
CREATE TABLE IF NOT EXISTS analyst_estimates (
    symbol VARCHAR(50) PRIMARY KEY REFERENCES assets(symbol) ON DELETE CASCADE,
    target_high NUMERIC(18, 4),
    target_low NUMERIC(18, 4),
    target_mean NUMERIC(18, 4),
    target_median NUMERIC(18, 4),
    target_currency VARCHAR(10) DEFAULT 'USD',
    recommendations JSONB DEFAULT '[]'::jsonb,         -- Son ayların Strong Buy/Buy/Hold/Sell dağılımı
    earnings_surprises JSONB DEFAULT '[]'::jsonb,      -- Son 4 çeyreğin EPS sürprizleri
    source_name VARCHAR(50) NOT NULL DEFAULT 'Finnhub',
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5. Skor ve Sinyal Sonuçları Tablosu (Bölüm 8 & 10)
CREATE TABLE IF NOT EXISTS score_results (
    symbol VARCHAR(50) PRIMARY KEY REFERENCES assets(symbol) ON DELETE CASCADE,
    composite_score NUMERIC(5, 2) NOT NULL,            -- 1.00 - 5.00
    confidence_level VARCHAR(20) NOT NULL,             -- HIGH, MEDIUM, LOW
    signal VARCHAR(30) NOT NULL,                       -- STRONG_BUY, BUY, HOLD, WATCH, SELL, STRONG_SELL
    coverage NUMERIC(5, 4) NOT NULL,                   -- 0.0000 - 1.0000
    
    category_scores JSONB NOT NULL DEFAULT '{}'::jsonb, -- 5 ana kategori ve alt metrik puanları
    
    altman_z_score NUMERIC(10, 4),                     -- Referans dayanıklılık skoru
    piotroski_f_score SMALLINT,                        -- 0 - 9 puan
    
    raw_score_before_hysteresis NUMERIC(5, 2),
    hysteresis_applied BOOLEAN NOT NULL DEFAULT FALSE,
    formula_version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    as_of_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    flags JSONB NOT NULL DEFAULT '[]'::jsonb,          -- Teşhis bayrakları
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_score_composite ON score_results(composite_score DESC);
CREATE INDEX IF NOT EXISTS idx_score_signal ON score_results(signal);
CREATE INDEX IF NOT EXISTS idx_score_confidence ON score_results(confidence_level);

-- 6. Tarama Çalışma ve İlerleme Kayıtları (Bölüm 9 & 10.5)
CREATE TABLE IF NOT EXISTS scan_runs (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stage VARCHAR(50) NOT NULL,                        -- INIT, MARKET_DATA, FINANCIALS, SCORING, BENCHMARKS, COMPLETED, FAILED
    status VARCHAR(30) NOT NULL,                       -- RUNNING, COMPLETED, FAILED
    total_assets INT NOT NULL DEFAULT 0,
    processed_assets INT NOT NULL DEFAULT 0,
    failed_assets INT NOT NULL DEFAULT 0,
    current_stage_description TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    duration_ms BIGINT,
    error_summary JSONB DEFAULT '[]'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_scan_runs_status ON scan_runs(status);
CREATE INDEX IF NOT EXISTS idx_scan_runs_started ON scan_runs(started_at DESC);
