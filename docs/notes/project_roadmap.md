# Project Roadmap

This roadmap outlines the phases for building the finance data engineering project.  
Scope: ingest ~100–200 tickers from yfinance at 1-minute granularity, process them daily, and store in a structured data lake.  
Style: local, free-first stack, with optional extensions for scale and interview showcase.  
Design decisions are cross-referenced with [Design Decisions](design_decisions.md).

---

## ADR Cross-Links by Phase

- **Phase 0 — Repo & Scaffolding** → ADR-0001 (Airflow), ADR-0002 (Parquet)  
- **Phase 1 — Ingestion MVP** → ADR-0002 (Parquet), ADR-0003 (Partitioning), ADR-0004 (Scheduling)  
- **Phase 2 — Data Quality & Lineage** → ADR-0001 (Airflow for GX integration)  
- **Phase 3 — Refinement & Feature Marts** → ADR-0002 (Parquet), ADR-0003 (Partitioning)  
- **Phase 4 — Query & Analytics** → ADR-0002 (Parquet compatibility with DuckDB)  
- **Phase 5 — Scale to 100–200 Tickers** → ADR-0001 (Airflow scalability), ADR-0003 (Partitioning efficiency), ADR-0004 (Scheduling)  
- **Phase 6 — Observability & SLAs** → ADR-0001 (Airflow SLAs), ADR-0004 (Scheduling impact on SLAs)  
- **Phase 7 — IaC & Cloud-Parity Demos** → ADR-0001 (Airflow portability), ADR-0002 (Parquet cloud-compatibility)  
- **Phase 8 — Real-time Showcase (optional)** → ADR-0003 (Partitioning for streaming writes)  

---

## Phase 0 — Repo & Scaffolding (1–2 days)
**Goal:** runnable local stack.  

- Create mono-repo:  
  - `orchestration/` (Airflow)  
  - `apps/` (extract, refine, dq)  
  - `infra/` (Terraform)  
  - `docker/`  
  - `tests/`  
- Compose file stands up Airflow + MinIO + optional DuckDB CLI + LocalStack.  
- `.env` file for secrets (tickers list, market hours, MinIO creds).  

---

## Phase 1 — Ingestion MVP (2–3 days)
**Goal:** fetch & store 1-min bars for 5–10 tickers.  

- Python extractor: paginate tickers, download latest 7 days of 1-minute data, idempotent upsert by `(ticker, ts)`.  
- Write to MinIO as partitioned Parquet; add compaction job (merge small files by day).  
- Airflow DAG: daily at market close + on-demand backfill.  
- Persist an ingestion audit log (rows written, duplicates removed, time range).  

**Theory notes:**  
- yfinance 1m data is limited; daily persistence accumulates history.  
- Micro-batches mitigate API hiccups and keep retry windows small.  

---

## Phase 2 — Data Quality & Lineage (2 days)
**Goal:** automated checks & reports.  

- Great Expectations suite:  
  - not-nulls, ranges, monotonic timestamps  
  - daily row count thresholds per ticker  
  - duplicate index = 0  
- Fail the DAG (or `soft_fail`) when critical tests break.  
- Store HTML validation reports.  

---

## Phase 3 — Refinement & Feature Marts (2–3 days)
**Goal:** clean silver and analytics-ready gold.  

- Time-zone normalize to UTC; align to exchange hours; forward-fill only within session.  
- Compute rolling features; write gold tables.  
- Add unit tests for time windows and feature math.  

---

## Phase 4 — Query & Analytics (1–2 days)
**Goal:** interactive SQL without server cost.  

- Wire DuckDB to query Parquet on MinIO paths.  
- Example: `read_parquet('s3://.../*.parquet')`.  
- Optional: ClickHouse for time-series features (materialized views, aggregating merges).  

---

## Phase 5 — Scale to 100–200 Tickers (1–2 days)
**Goal:** stable daily runs.  

- Parallelize per-ticker tasks with Airflow TaskGroups or dynamic task mapping.  
- Add rate-limit backoff respecting yfinance constraints; rotate batches.  
- Add file compaction by ticker/day to keep object counts sane.  

---

## Phase 6 — Observability & SLAs (1 day)
**Goal:** production polish.  

- Airflow SLAs; custom logs & metrics (rows ingested, late data, GX failures).  
- Storage lifecycle policy:  
  - keep bronze raw indefinitely  
  - compact silver monthly  

---

## Phase 7 — IaC & Cloud-Parity Demos (1–2 days)
**Goal:** interview leverage.  

- Terraform modules targeting LocalStack S3/IAM locally.  
- Document AWS mapping:  
  - MinIO → S3  
  - Airflow → MWAA  
  - DuckDB → Athena (conceptually)  
  - GX → Data Quality jobs  
  - Docker images → ECR/ECS  
- Keep execution local to remain free.  

---

## Phase 8 — “Real-time” Showcase (optional, 1–2 days)
**Goal:** demonstrate streaming skills without paid market feeds.  

- Re-play the latest day’s 1-minute bars into Kafka/Redpanda at 60x speed.  
- Process with Spark Structured Streaming to compute running VWAP & alerts.  
- Sink results to gold layer.  

---
