from __future__ import annotations

import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Iterable

from pyspark.sql import SparkSession, functions as F

from src.transforms.transform_to_silver import (
    load_cfg,
    build_spark,
    infer_date_category_ticker,
    standardize_cols,
    enforce_schema,
    add_metadata,
    validate_and_filter,
    write_silver,
)




# ----------------- helpers -----------------
def iter_parquet_files(base: Path, date: str, category: str | None = None) -> Iterable[Path]:
    """
    Yield Parquet files under:
      data/bronze/<YYYY_MM_DD>/<category>/*.parquet
    If category is None, process all categories for that date.
    """
    root = base / date
    if not root.exists():
        raise FileNotFoundError(f"Bronze date folder not found: {root}")

    cats = [category] if category else [p.name for p in root.iterdir() if p.is_dir()]
    for cat in cats:
        cat_dir = root / cat
        if not cat_dir.exists():
            logger.warning("Category folder missing: %s", cat_dir)
            continue
        for path in cat_dir.glob("*.parquet"):
            yield path


def profile_spark(df):
    """Return {'min_ts': ..., 'max_ts': ..., 'rows': ...} using Spark-native ops."""
    row = (
        df.agg(
            F.min("datetime").alias("min_ts"),
            F.max("datetime").alias("max_ts"),
            F.count(F.lit(1)).alias("rows"),
        )
        .collect()[0]
    )
    return {"min_ts": row["min_ts"], "max_ts": row["max_ts"], "rows": int(row["rows"])}


def process_one(spark: SparkSession, bronze_path: Path, out_root: Path) -> dict:
    load_date, category, ticker = infer_date_category_ticker(bronze_path)

    # Read with Spark (same as your single-file transform)
    df = spark.read.parquet(str(bronze_path))
    df = standardize_cols(df)
    df = enforce_schema(df)
    df = add_metadata(df, load_date, category, ticker)
    df = validate_and_filter(df)

    prof = profile_spark(df)
    out_path = write_silver(df, out_root, load_date, category, ticker)

    result = {
        "ticker": ticker,
        "category": category,
        "date": load_date,
        "rows": prof["rows"],
        "min_ts": str(prof["min_ts"]),
        "max_ts": str(prof["max_ts"]),
        "out": str(out_path),
    }
    return result



def append_run_log_to_pg(spark, res: dict, cfg: dict):
    url  = cfg.get("jdbc_url", "jdbc:postgresql://postgres:5432/yfinance")
    user = cfg.get("jdbc_user", "yfinance_app")
    pwd  = cfg.get("jdbc_password", "password")

    # res has strings for min_ts/max_ts; cast to timestamp in Spark
    sdf = spark.createDataFrame([res])
    out = (sdf.selectExpr(
                "current_timestamp() AS run_ts",
                "CAST(date AS string) AS load_date",
                "CAST(category AS string) AS category",
                "CAST(ticker AS string) AS ticker",
                "CAST(rows AS int) AS rows",
                "CAST(min_ts AS timestamp) AS min_ts",
                "CAST(max_ts AS timestamp) AS max_ts",
                "CAST(out AS string) AS out_path"
           ))
    (out.write
        .mode("append")
        .format("jdbc")
        .option("url", url)
        .option("dbtable", "silver_run_log")
        .option("user", user)
        .option("password", pwd)
        .option("driver", "org.postgresql.Driver")
        .save())



# ----------------- main -----------------
def main():
        
    if len(sys.argv) < 2:
        print("Usage: python -m src.transforms.run_silver_batch <YYYY_MM_DD> [category] [out_root]")
        sys.exit(1)

    date = sys.argv[1]
    category = sys.argv[2] if len(sys.argv) > 2 else None
    out_root = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("data/silver")

    bronze_root = Path("data/bronze")
    cfg = load_cfg()
    spark = build_spark(cfg)

    # ----------------- logging -----------------
    LOG_PATH = Path(f"data/silver/{date}.log")
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("silver_batch")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = RotatingFileHandler(LOG_PATH, maxBytes=512_000, backupCount=3)
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(handler)
        
        
    ok, fail = 0, 0
    try:
        for p in iter_parquet_files(bronze_root, date, category):
            try:
                res = process_one(spark, p, out_root)
                ok += 1
                logger.info(
                    "OK | %(date)s | %(category)s | %(ticker)s | rows=%(rows)s | %(min_ts)s → %(max_ts)s | %(out)s",
                    res,
                )
                print(f"OK   {res['date']} {res['category']} {res['ticker']} rows={res['rows']} -> {res['out']}")
                append_run_log_to_pg(spark, res, cfg) 
            except Exception as e:
                fail += 1
                logger.error("FAIL | %s | %s", p, e)
                print(f"FAIL {p} | {e}")
    finally:
        spark.stop()

    print(f"\nSummary: ok={ok} fail={fail} | log: {LOG_PATH}")


if __name__ == "__main__":
    main()


