# Storage Strategy

## Purpose
Define how data is organized, stored, and optimized for scalability and performance in the data lake.

---

## Lake Layout

`bronze/{dataset}/symbol=XYZ/date=YYYY-MM-DD/`
`silver/{dataset}/symbol=XYZ/date=YYYY-MM-DD/`
`gold/{mart}/date=YYYY-MM-DD/`


- **Bronze:** raw ingested data, minimally processed.  
- **Silver:** cleaned and standardized data, schema-enforced.  
- **Gold:** curated aggregates and business-level metrics.  

---

## Partitioning
- **Primary:** `symbol`  
- **Secondary:** `date`  
- Enables efficient pruning for symbol- and date-range queries.  
- Balances parallelism with manageable file counts.  

---

## File Format
- **Parquet** for all layers.  
  - Columnar → efficient for analytics.  
  - Compression → reduced storage cost.  
  - Schema evolution → supports additive changes safely.  

---

## File Size Targets
- Aim for **64–256 MB per Parquet file**.  
- Too small → many tiny files = metadata overhead.  
- Too large → slow single-threaded reads.  

---

## Schema Evolution
- **Additive changes only** (adding columns is safe).  
- Breaking changes (renaming/dropping columns) require versioning or backfills.  
- Contracts between layers must be enforced.  

---

## Naming Conventions
- Use lowercase, snake_case for columns.  
- Dataset folder names reflect business domain (e.g., `quotes`, `daily_bars`).  
- Partition folders are explicit (`symbol=TSLA/date=2025-09-02`).  

---

## Retention Policy
- **Bronze:** keep for 6–12 months (optional pruning for cost).  
- **Silver/Gold:** long-term retention (primary source for analytics).  

---

## Implementation Pointers
- Data written by Airflow DAGs → `dags/`  
- Silver/Gold transforms → `jobs/`  
- Storage path controlled via configuration (e.g., Airflow Variables or env vars).  

---