
 # Design Decisions (ADRs -  Architecture Decision Records)

This document records major technical decisions, along with context, alternatives, and consequences.  
Each ADR also lists the roadmap phases where it is applied.

---

## ADR-0001: Use Airflow for Orchestration
**Context**  
We need a scheduler and orchestrator to manage dependencies, retries, and backfills.  

**Decision**  
Adopt **Apache Airflow (OSS)** for DAG-based orchestration.  

**Consequences**  
- ✅ Rich scheduling, retries, SLAs, and UI.  
- ✅ Strong community, extensibility, Python-native.  
- ⚠️ Requires some operational overhead (webserver, scheduler, metadata DB).  

**Alternatives**  
- Prefect (lighter, Pythonic, but cloud features cost).  
- Dagster (modern, strong typing, but less mature in free tier).  

**Roadmap phases impacted**  
- **Phase 0:** Repo & Scaffolding (set up orchestration folder, docker-compose with Airflow).  
- **Phase 1:** Ingestion MVP (daily DAG, backfill DAG).  
- **Phase 2:** Data Quality & Lineage (DAG integration with GX checks).  
- **Phase 5:** Scale to 100–200 tickers (parallel tasks, TaskGroups).  
- **Phase 6:** Observability & SLAs (Airflow SLAs, logs).  
- **Phase 7:** IaC & Cloud-parity demos (Airflow → MWAA mapping).  

---

## ADR-0002: Use Parquet as the Storage Format
**Context**  
We need an efficient format for storing OHLCV time-series at scale.  

**Decision**  
Store all layers (bronze, silver, gold) as **Parquet** files.  

**Consequences**  
- ✅ Columnar compression and predicate pushdown → reduced cost + faster queries.  
- ✅ Widely supported across Spark, Pandas, Presto, etc.  
- ⚠️ Must manage schema evolution carefully.  

**Alternatives**  
- CSV (simple but inefficient).  
- Delta Lake / Iceberg / Hudi (advanced features, but add complexity to a free-first stack).  

**Roadmap phases impacted**  
- **Phase 0:** Repo & Scaffolding (decide on Parquet from start).  
- **Phase 1:** Ingestion MVP (bronze written as Parquet).  
- **Phase 3:** Refinement & Feature Marts (silver/gold written as Parquet).  
- **Phase 4:** Query & Analytics (DuckDB queries Parquet directly).  
- **Phase 7:** IaC & Cloud-parity demos (Parquet compatibility with Athena/S3).  

---

## ADR-0003: Partition by `symbol` and `date`
**Context**  
Query patterns are symbol-based and time-based.  

**Decision**  
Partition datasets by **symbol** and **date**.  

**Consequences**  
- ✅ Efficient pruning for symbol/date queries.  
- ✅ Simplifies reruns (overwrite single partition).  
- ⚠️ May lead to many small files if not tuned.  

**Alternatives**  
- Partition only by date (simpler, but symbol-level scans become expensive).  
- Partition only by symbol (good for one symbol, bad for time range queries).  

**Roadmap phases impacted**  
- **Phase 1:** Ingestion MVP (bronze layer writes partitioned by symbol/date).  
- **Phase 3:** Refinement & Feature Marts (silver/gold partitioned by symbol/date).  
- **Phase 5:** Scale to 100–200 tickers (ensures efficient reads/writes).  
- **Phase 8:** Real-time Showcase (streaming writes still partition-compatible).  

---

## ADR-0004: Scheduling Strategy
**Context**  
We want resilience to missing/late data without needing real-time streaming.  

**Decision**  
Run **daily at 07:00 UTC**, backfilling the previous 7 days of data.  

**Consequences**  
- ✅ Resilient to weekends, holidays, or outages.  
- ✅ Idempotent (safe reruns).  
- ⚠️ Not suitable for ultra-low latency use cases (intraday).  

**Alternatives**  
- Continuous streaming ingestion (complex, not free).  
- EOD-only daily snapshot (lighter, but loses intraday granularity).  

**Roadmap phases impacted**  
- **Phase 1:** Ingestion MVP (DAG scheduled daily + backfills).  
- **Phase 5:** Scale to 100–200 tickers (parallel scheduling).  
- **Phase 6:** Observability & SLAs (SLAs tied to daily runs).  

---
