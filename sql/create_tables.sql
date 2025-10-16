-- --- Namespaces ---
CREATE SCHEMA IF NOT EXISTS meta;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- --- meta: ingestion logs (one row per ticker attempt) ---
CREATE TABLE IF NOT EXISTS meta.ingestions (
  ingestion_id   BIGSERIAL PRIMARY KEY,
  run_ts_utc     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  ticker         TEXT NOT NULL,
  category       TEXT,
  file_path      TEXT NOT NULL,
  status         TEXT NOT NULL CHECK (status IN ('SUCCESS','FAILED')),
  rows_written   INTEGER,
  error_message  TEXT
);
CREATE INDEX IF NOT EXISTS ix_ingestions_run_ts_utc ON meta.ingestions (run_ts_utc DESC);
CREATE INDEX IF NOT EXISTS ix_ingestions_ticker      ON meta.ingestions (ticker);

-- --- silver: curated minute bars (serving copy of Parquet silver) ---
CREATE TABLE IF NOT EXISTS silver.bars_1m (
  ticker   TEXT        NOT NULL,
  ts_utc   TIMESTAMPTZ NOT NULL,
  open     DOUBLE PRECISION,
  high     DOUBLE PRECISION,
  low      DOUBLE PRECISION,
  close    DOUBLE PRECISION,
  volume   BIGINT,
  PRIMARY KEY (ticker, ts_utc)
);
CREATE INDEX IF NOT EXISTS ix_bars_1m_ticker_ts ON silver.bars_1m (ticker, ts_utc);

-- --- gold: features/aggregates (small, query-friendly) ---
CREATE TABLE IF NOT EXISTS gold.features_1m (
  ticker   TEXT        NOT NULL,
  ts_utc   TIMESTAMPTZ NOT NULL,
  ret_1m   DOUBLE PRECISION,
  vwap_5m  DOUBLE PRECISION,
  roll_vol_30m DOUBLE PRECISION,
  PRIMARY KEY (ticker, ts_utc)
);
CREATE INDEX IF NOT EXISTS ix_features_1m_ticker_ts ON gold.features_1m (ticker, ts_utc);

CREATE TABLE IF NOT EXISTS gold.daily_agg (
  ticker        TEXT NOT NULL,
  trading_date  DATE NOT NULL,
  o DOUBLE PRECISION,
  h DOUBLE PRECISION,
  l DOUBLE PRECISION,
  c DOUBLE PRECISION,
  vwap_day      DOUBLE PRECISION,
  vol_day       BIGINT,
  gap_count     INTEGER,
  PRIMARY KEY (ticker, trading_date)
);
CREATE INDEX IF NOT EXISTS ix_daily_agg_ticker_date ON gold.daily_agg (ticker, trading_date);



CREATE TABLE IF NOT EXISTS public.silver_run_log (
  id BIGSERIAL PRIMARY KEY,
  run_ts TIMESTAMPTZ DEFAULT now(),
  load_date TEXT NOT NULL,
  category  TEXT NOT NULL,
  ticker    TEXT NOT NULL,
  rows      INT  NOT NULL,
  min_ts    TIMESTAMPTZ,
  max_ts    TIMESTAMPTZ,
  out_path  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_silver_run_log ON public.silver_run_log(load_date, category, ticker);



CREATE TABLE IF NOT EXISTS public.gold_daily_ohlc (
  ticker   TEXT NOT NULL,
  category TEXT NOT NULL,
  date     DATE NOT NULL,
  open     DOUBLE PRECISION,
  high     DOUBLE PRECISION,
  low      DOUBLE PRECISION,
  close    DOUBLE PRECISION,
  volume   BIGINT,
  daily_return DOUBLE PRECISION,
  PRIMARY KEY (ticker, date, category)
);
