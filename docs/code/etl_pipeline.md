# ETL Pipeline

## Goal
A free, reliable daily pipeline that ingests ~100–200 tickers from yfinance at 1-minute granularity, lands **bronze** raw data, curates **silver** cleaned data, and publishes **gold** aggregates for analytics.

---

## Why this stack
- **Airflow (OSS):** code-first DAGs, retries, backfills, SLAs, plugins. Excellent for dependency management and observability.  
- **yfinance (free):** quick access to historical OHLCV. Works for a daily backfill strategy when intraday recency isn’t critical.  
- **Parquet (free, columnar):** compression + predicate pushdown → lower storage and faster reads versus CSV.  
- **PySpark (free):** scalable transforms for joins/aggregations at 100–1,000 symbols over long horizons.  

---

## Data Flow (high level)

**Ingest (Bronze):**  
- Fetch 1m bars per symbol for a rolling window (e.g., last 7 days).  
- Write one Parquet file per symbol per day under `/bronze/quotes/symbol=XXX/date=YYYY-MM-DD/`.  

**Clean/Conform (Silver):**  
- Normalize schema/types/timezone  
- Deduplicate `(symbol, timestamp)`  
- Fill obvious data gaps if needed  

**Publish (Gold):**  
- Daily aggregates per symbol (OHLCV, VWAP, simple returns)  
- Optional: rolling 5/20-day indicators  

---

## Lake Layout

`bronze/quotes/symbol=TSLA/date=2025-09-02/part-000.parquet`
`silver/quotes/symbol=TSLA/date=2025-09-02/part-000.parquet`
`gold/daily_bars/date=2025-09-02/part-000.parquet?`


**Why partition by symbol and date:**  
Fast pruning for symbol- and date-range scans; simple checkpointing and reruns.

---

## Scheduling Strategy
- **Daily at 07:00 UTC** (before EU workday): pull the previous 7 days of 1-minute bars to cover weekends/holidays & late data.  
- **Idempotency:** overwrite same partitions on reruns (safe because files are partitioned by date).  
- **Backfill:** enable a “catchup” window (e.g., last 30 days) on demand with a parameter or backfill task.  

---

## Notes
- Pure Python + yfinance + pandas keeps ingestion simple and free.  
- When data grows, switch the **silver** and **gold** steps to PySpark for speed.  

---

## Observability & Quality
- Row counts per `(symbol, date)` partition; alert if counts deviate.  
- Schema contract for bronze → silver (types + required columns).  
- Latency metrics: ingestion start/end, silver/gold job durations.  
- Airflow SLAs on the `quotes_daily` DAG.  

---

## Idempotency & Reruns
- Overwrite per partition every run → safe to re-run yesterday or the last 7 days.  
- Deterministic file paths ensure no orphaned data on retry.  

---

## Scaling Up (100 → 1,000 tickers)
- Batch symbols (e.g., chunks of 100 per task) or break by TaskGroup per 200 symbols.  
- Use Spark cluster for transforms (local dev → standalone/YARN later).  
- Tune file sizes (64–256 MB per Parquet file) via repartitioning.  

---

## Local Development Defaults (free)
- Use local filesystem for the lake path.  
- If you want S3 semantics locally: MinIO (free) later, not required to start.  

---

## References
- [Airflow Concepts](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/index.html)  
- [yfinance Docs](https://pypi.org/project/yfinance/)  
- [Parquet Format](https://parquet.apache.org/docs/)  