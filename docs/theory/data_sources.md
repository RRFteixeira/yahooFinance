# Data Sources

## Purpose
Document the financial data sources considered for this project, with their advantages, limitations, and how they fit into the pipeline.

---

## yfinance
- ✅ Free and easy to use (Python package)  
- ✅ Supports OHLCV with intraday granularity (1m, but limited history)  
- ⚠️ 1-minute data only available for ~7 days back  
- ⚠️ Rate limits not clearly documented → need retry/backoff strategies  

**Use in project:**  
- Primary ingestion source for Bronze layer  
- Combined with daily persistence to build historical archive  

---

## Design Decision References
- Linked to [ADR-0002: Use Parquet](../notes/design_decisions.md#adr-0002-use-parquet-as-storage-format) (applies regardless of data source)  
- Linked to [ADR-0004: Scheduling Strategy](../notes/design_decisions.md#adr-0004-scheduling-strategy) (retries, backfills depend on source limits)  

---

