from __future__ import annotations

import sys
from pathlib import Path
import datetime as dt
import yaml

from pyspark.sql import SparkSession, functions as F, types as T


# ----------------- config -----------------
def load_cfg(path: str = "config/spark_config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def build_spark(cfg: dict) -> SparkSession:
    builder = (
        SparkSession.builder
        .appName(cfg.get("app_name", "yahoo-silver"))
        .master(cfg.get("master", "local[2]"))
        .config("spark.sql.shuffle.partitions", cfg.get("shuffle_partitions", 4))
        .config("spark.sql.parquet.compression.codec", cfg.get("parquet_compression", "snappy"))
        .config("spark.driver.host", cfg.get("driver_host", "127.0.0.1"))
        .config("spark.driver.bindAddress", cfg.get("driver_bind", "127.0.0.1"))
    )
    
    if cfg.get("spark_jars_packages"):
        builder = builder.config("spark.jars.packages", cfg["spark_jars_packages"])
    return builder.getOrCreate()


# ----------------- helpers -----------------
def infer_date_category_ticker(bronze_path: Path) -> tuple[str, str, str]:
    """
    Expect: data/bronze/YYYY_MM_DD/<category>/<ticker>[_prices].parquet
    """
    parts = bronze_path.parts
    try:
        i = parts.index("bronze")
    except ValueError:
        raise RuntimeError(f"'bronze' folder not found in path: {bronze_path}")

    load_date = parts[i + 1]
    category = parts[i + 2]
    ticker = Path(parts[-1]).stem  # e.g., "META" or "META_prices"

    return load_date, category, ticker


def standardize_cols(df):
    # Rename common Yahoo columns to snake_case (idempotent)
    mapping = {
        "Datetime": "datetime",
        "Date": "datetime",        # daily data variant
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "adj_close",
        "AdjClose": "adj_close",
        "Volume": "volume",
    }
    for old, new in mapping.items():
        if old in df.columns:
            df = df.withColumnRenamed(old, new)
    return df


def enforce_schema(df):
    wanted = {
        "datetime": T.TimestampType(),
        "open": T.DoubleType(),
        "high": T.DoubleType(),
        "low": T.DoubleType(),
        "close": T.DoubleType(),
        "adj_close": T.DoubleType(),
        "volume": T.LongType(),
    }
    for col, typ in wanted.items():
        if col in df.columns:
            df = df.withColumn(col, F.col(col).cast(typ))
    return df


def add_metadata(df, load_date: str, category: str, ticker: str):
    return (
        df.withColumn("load_date", F.lit(load_date))             # e.g. "2025_09_27"
          .withColumn("category", F.lit(category))               # e.g. "digital_media"
          .withColumn("ticker", F.lit(ticker))                   # e.g. "META"
          .withColumn("source_system", F.lit("YahooFinance"))
          .withColumn("ingest_ts", F.current_timestamp())
          .withColumn("date", F.to_date("datetime"))
    )


def validate_and_filter(df):
    # Count issues, then keep only valid rows
    null_dt = df.filter(F.col("datetime").isNull()).count()
    neg_px = df.filter(
        (F.col("open") < 0) | (F.col("high") < 0) | (F.col("low") < 0) | (F.col("close") < 0)
    ).count()

    valid = df.filter(
        F.col("datetime").isNotNull()
        & (F.col("open") >= 0)
        & (F.col("high") >= 0)
        & (F.col("low") >= 0)
        & (F.col("close") >= 0)
    )

    print(f"[VALIDATION] null_datetime={null_dt}, negative_prices={neg_px}, kept_rows={valid.count()}")
    return valid


def write_silver(df, out_root: Path, load_date: str, category: str, ticker: str) -> Path:
    out_path = out_root / load_date / category / f"{ticker}.parquet"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # One file per ticker for easy manual inspection in dev
    (df.coalesce(1)
       .write
       .mode("overwrite")
       .parquet(str(out_path)))
    return out_path


# ----------------- main -----------------
def main(bronze_file: str, out_root: str = "data/silver"):
    cfg = load_cfg()
    spark = build_spark(cfg)

    bronze_path = Path(bronze_file)
    load_date, category, ticker = infer_date_category_ticker(bronze_path)

    df = spark.read.parquet(str(bronze_path))
    df = standardize_cols(df)
    df = enforce_schema(df)
    df = add_metadata(df, load_date, category, ticker)
    df = validate_and_filter(df)

    # quick profile
    row = (
        df.agg(
            F.min("datetime").alias("min_ts"),
            F.max("datetime").alias("max_ts"),
            F.count(F.lit(1)).alias("rows"),
        )
        .collect()[0]
    )
    prof = {"min_ts": row["min_ts"], "max_ts": row["max_ts"], "rows": row["rows"]}
    print(f"[PROFILE] {ticker} | {category} | {load_date} -> {prof}")

    out_path = write_silver(df, Path(out_root), load_date, category, ticker)
    print(f"[WRITE] {out_path}")

    spark.stop()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.transforms.transform_to_silver <bronze_parquet_file> [out_root]")
        sys.exit(1)
    bronze = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "data/silver"
    main(bronze, out)

