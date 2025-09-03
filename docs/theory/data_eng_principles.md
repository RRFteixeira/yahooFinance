# Data Engineering Principles

## Purpose
Capture core concepts that guide the design of this finance data pipeline, ensuring it is reliable, scalable, and free-first.

---

## ETL vs ELT
- **ETL (Extract → Transform → Load):** good fit when transformations are heavy and need orchestration before landing.  
- **ELT (Extract → Load → Transform):** often used in cloud warehouses; less relevant here since we store Parquet in a lake.  
- **Decision:** ETL approach via Airflow + PySpark.  

---

## Batch vs Streaming
- **Batch:** predictable, easier to run free (daily pulls).  
- **Streaming:** real-time, but requires continuous API access (usually paid).  
- **Decision:** batch-first (Phase 1–7), optional simulated streaming (Phase 8).  

---

## Partitioning & File Strategy
- Partition by `symbol` and `date` (see [ADR-0003](../notes/design_decisions.md#adr-0003-partition-by-symbol-and-date)).  
- Target **64–256 MB Parquet files** → balance I/O vs metadata overhead.  
- Use compaction jobs to merge small files.  

---

## Schema Evolution
- Start minimal: `symbol`, `timestamp`, `open`, `high`, `low`, `close`, `volume`.  
- Add new columns only (non-breaking).  
- Breaking changes → new dataset version.  

---

## Observability
- **Row counts per partition** to catch missing data.  
- **Schema contracts** between Bronze → Silver → Gold.  
- **SLAs in Airflow** to enforce timeliness.  

---
