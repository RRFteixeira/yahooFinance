# 📝 Design Decisions

This file documents the reasoning behind key design and technology choices.

---

## Phase 0
- **Repository structure** was created to separate code (`apps/`), theory (`theory/`), documentation (`notes/`), and tests (`tests/`).
- **Python virtual environment** (`venv/`) is used for dependency isolation.
- **Minimal dependencies** (`yfinance`, `pandas`, `pytest`) ensure a lightweight start.
- **Version control** with Git is in place to track evolution across phases.

Future phases will include decisions for:
- Database schema design
- Storage format choices (Parquet vs Delta Lake)
- Orchestration (Airflow) and infrastructure (Docker/Terraform)