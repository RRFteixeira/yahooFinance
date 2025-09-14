Course Roadmap: Finance Minute-Bars Platform (100–200 tickers, yfinance)
Phase 0 — Orientation & guardrails (0.5 day)

Why now: Set expectations and constraints so later choices make sense.
Concepts: minute-data lookback limits; reproducibility; project artifacts.
You’ll do:

Define your ticker universe (start with 10, grow later).

Decide time boundaries (UTC vs exchange local; store UTC).

Create a data dictionary (OHLCV, primary keys (ticker, ts)).

Document the yfinance 1-minute constraint: short lookback; you must persist daily to build a year.
Success criteria: A short README with scope, tickers, timezones, column definitions, and constraints.
Artifacts: docs/scope.md, docs/data_dictionary.md.

Phase 1 — Pure Python exploration (0.5–1 day)

Feature: See 1-minute data in a DataFrame and do simple profiling.
New thing: None (just Python + pandas).
Why: Build intuition about the raw shape, quality, and gaps.
You’ll do:

Fetch one ticker, one day, inspect columns, nulls, duplicates.

Compute basic stats (row counts during market hours; min/max ts).
Success criteria: You can clearly describe what a “good” daily file looks like.
Artifacts: notebooks/01_explore_yf.ipynb, docs/findings_phase1.md.

Phase 2 — Git discipline & project skeleton (0.5 day)

Feature: Reproducible repo with clear structure.
New thing: Version control habits; project layout.
Why: Each later phase depends on a stable structure.
You’ll do:

Create a simple src/ layout and tests/ folder.

Add requirements.txt and a minimal .env.example.

Adopt conventional commits and a lightweight branching flow.
Success criteria: Another developer can clone and run Phase 1 steps.
Artifacts: CONTRIBUTING.md, Makefile (optional), README badges.

Phase 3 — Postgres in Docker (DB only) (0.5–1 day)

Feature: A running Postgres instance you can connect to.
New thing: Docker (but only for the database).
Why: Isolate storage early; avoid local conflicts; learn Docker by doing just one service.
You’ll do:

Start Postgres in Docker with a non-default port and a named volume.

Verify connectivity using psql or a GUI client.
Success criteria: You can connect, create a schema, and list tables.
Artifacts: docker/compose.db.yml, docs/db_setup.md.

Phase 4 — Data modeling for minute bars (0.5 day)

Feature: Schema that supports idempotent inserts and time-based queries.
New thing: SQL schema design & indexing strategies.
Why: Relational modeling skills are core to data engineering.
You’ll do:

Design a canonical table bars_1m with PK (ticker, ts).

Add sensible indexes (e.g., (ticker, ts) B-tree).
Success criteria: You can explain why the PK prevents duplicates and supports upserts.
Artifacts: db/schema.sql, docs/modeling_decisions.md.

Phase 5 — Persist to Postgres (1 day)

Feature: Load minute bars into Postgres reliably.
New thing: Idempotent write patterns (UPSERT/MERGE).
Why: Prevent duplicates across daily runs.
You’ll do:

Write a minimal ingest script that:

Fetches last N days of 1-minute bars for a small ticker set.

Performs UPSERT keyed by (ticker, ts).

Tracks a simple load_audit table (rows inserted/updated, start/end time).
Success criteria: Re-running the script doesn’t change row counts (idempotent).
Artifacts: docs/runbook_ingest.md, db/load_audit.sql.

Phase 6 — Lightweight orchestration (0.5 day)

Feature: Automatic daily run without Airflow.
New thing: OS scheduler (Windows Task Scheduler or cron).
Why: Learn scheduling basics before Airflow’s DAG model.
You’ll do:

Schedule the Phase 5 script to run once per weekday after market close.

Add a log file per run and simple email/console notifications.
Success criteria: A run happens on schedule and writes to load_audit.
Artifacts: docs/scheduling_basics.md.

Phase 7 — Data quality v1 (0.5 day)

Feature: Gate bad loads with basic checks.
New thing: DQ mindset before frameworks.
Why: Quality is a product requirement, not an afterthought.
You’ll do:

Pre-load checks: expected column set; timestamp monotonicity; row count threshold.

Post-load checks: duplicates in DB; negative volume guard.
Success criteria: Bad data prevents promotion; you get a clear fail message.
Artifacts: docs/dq_checklist.md.

Phase 8 — Parquet lake (bronze) on local disk (1 day)

Feature: Store the exact raw pulls as Parquet side-by-side with the DB.
New thing: Columnar files & partitioning on local filesystem (no object store yet).
Why: Introduce lake concepts without S3 complexity.
You’ll do:

Write day-partitioned Parquet: data/bronze/interval=1m/ticker=XYZ/date=YYYY-MM-DD/*.parquet.

Add a tiny compaction step (combine tiny files for the day).
Success criteria: You can query a day of Parquet quickly and compare counts to DB.
Artifacts: docs/storage_strategy.md.

Phase 9 — Analytical SQL with DuckDB (0.5–1 day)

Feature: Explore Parquet with SQL instantly.
New thing: DuckDB querying over local Parquet.
Why: Demonstrate lake-query skills with zero ops.
You’ll do:

Run ad-hoc queries: hourly averages, gaps per ticker, rolling 5-minute VWAP (conceptually).

Compare DB vs Parquet results for consistency.
Success criteria: Analyses return fast and match DB sanity checks.
Artifacts: notebooks/02_duckdb_analysis.ipynb.

Phase 10 — Airflow introduction (1 day)

Feature: Replace OS scheduler with a tiny DAG.
New thing: Airflow (Dockerized) with a single DAG and two tasks.
Why: Learn DAGs without the full stack.
You’ll do:

Run Airflow in Docker with only: Webserver, Scheduler, and a LocalExecutor.

Create a DAG with two tasks: fetch+write to Postgres, then write Parquet.
Success criteria: The DAG runs daily, shows success/metrics, and remains idempotent.
Artifacts: docs/airflow_basics.md.

Phase 11 — Data quality v2 (Great Expectations) (1 day)

Feature: Declarative expectations with HTML reports.
New thing: Great Expectations.
Why: Standards-based data contracts; visible documentation.
You’ll do:

Define expectations for nulls, ranges, duplicates, monotonic timestamps.

Wire a validation task in the Airflow DAG that can fail/soft-fail.
Success criteria: A failing expectation marks the run and stores a report.
Artifacts: docs/dq_expectations.md, gx/ reports folder.

Phase 12 — MinIO (S3-compatible) data lake (1 day)

Feature: Move Parquet from local disk to MinIO buckets.
New thing: Object storage semantics.
Why: Practice S3 patterns without cloud cost.
You’ll do:

Run MinIO with a single bucket market-micros.

Update paths to s3://market-micros/bronze/....

Verify reads via DuckDB with S3 config.
Success criteria: Same queries work; object counts and sizes look healthy.
Artifacts: docs/object_store_basics.md.

Phase 13 — Silver tables & transformations (1 day)

Feature: Cleaned minute bars (deduped, session-bounded, UTC).
New thing: Data contracts across Bronze → Silver → Gold.
Why: Professional layering and reprocessing.
You’ll do:

Define silver logic (dedupe by (ticker, ts), remove out-of-session, forward-fill within session only).

Write silver Parquet partitioned by date/ticker on MinIO.
Success criteria: Silver row counts and quality metrics meet thresholds.
Artifacts: docs/bronze_silver_gold.md.

Phase 14 — Gold features & marts (0.5–1 day)

Feature: Analytics-ready features (returns, rolling vol, VWAP).
New thing: Reusable transformations; documentation.
Why: Shows business-facing value.
You’ll do:

Produce a small gold dataset of features with clear column definitions.

Document use-cases (volatility by hour, liquidity screens).
Success criteria: A stakeholder can answer a question in minutes using gold.
Artifacts: docs/gold_catalog.md.

Phase 15 — Scaling to 100–200 tickers (0.5 day)

Feature: Parallel ingestion with guardrails.
New thing: Airflow dynamic task mapping or TaskGroup parallelism.
Why: Showcase scale tactics without overcomplication.
You’ll do:

Batch tickers (e.g., 25 per group) to respect rate limits.

Add retry backoff and jitter.
Success criteria: Daily runs complete within your time budget; load_audit remains clean.

Phase 16 — Observability polish (0.5 day)

Feature: Track SLAs and costs (local storage), and DQ drift.
New thing: Airflow SLAs + metrics.
Why: Production tone.
You’ll do:

Add SLAs on ingestion duration.

Emit simple metrics (rows, partitions written) to logs and a summary table.
Success criteria: You can explain yesterday’s run health in one minute.

Phase 17 — “Real-time” replay (optional, 1 day)

Feature: Simulated streaming from your latest day.
New thing: Kafka/Redpanda + micro-batch processing (can be Python or Spark later).
Why: Demonstrate real-time thinking without paid feeds.
You’ll do:

Replay a day’s minute bars at 60× into a topic; compute a running VWAP; store a rolling output.
Success criteria: A consumer reflects near-real-time feature updates.

Phase 18 — Spark sampler (optional, 1–2 days)

Feature: Batch transforms with Spark on your silver Parquet.
New thing: PySpark fundamentals (narrow/wide ops, partitions).
Why: Check the “Big Data” box with real transforms.
You’ll do:

Run Spark locally on a single machine; rewrite the gold features job in Spark.

Explain when Spark makes sense vs pandas/DuckDB.
Success criteria: Same outputs, with commentary on performance/partitions.

Phase 19 — Terraform + LocalStack (optional, 1 day)

Feature: IaC rehearsal, no cloud bills.
New thing: Terraform resources mapped to S3/IAM on LocalStack.
Why: Cloud-readiness narrative for interviews.
You’ll do:

Define bucket, policy, and a “job” placeholder (e.g., Lambda stub or Doc-only).

Show plan/apply/destroy and map to AWS equivalents.
Success criteria: You can walk through your IaC in 3 minutes.

Phase 20 — Capstone: reproducible demo (0.5 day)

Feature: One-command demo + narrative.
New thing: Storytelling.
Why: Interview impact.
You’ll do:

Write a demo script: bootstrap → ingest → DQ → refine → query → dashboard notebook.

Add a portfolio README with screenshots and a “what I’d do in production” section.
Success criteria: A reviewer can follow your story end-to-end in 10 minutes.

Grading rubric (self-assessment at each phase)

Concept clarity: You can explain the “why” in one paragraph.

Repeatability: Steps are documented and runnable by someone else.

Data integrity: No duplicates; sensible counts; checks pass.

Scale awareness: You can articulate the next bottleneck and mitigation.

Observability: There’s a place to look for health (logs, audits, reports).

Multiple paths you can take later

Warehouse path: Add ClickHouse for fast time-series aggregation instead of Postgres for analytics.

Delta path: Swap Parquet silver/gold to Delta Lake if you want ACID on lake.

Visualization path: Lightweight dashboard via Streamlit or a SQL notebook with DuckDB.

What stays free

Python, pandas, DuckDB, Postgres (Docker), MinIO, Airflow (Docker), Great Expectations, Kafka/Redpanda (community), Spark local, Terraform + LocalStack—all free locally.

Keep cloud as emulation only to avoid costs.