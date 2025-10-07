from __future__ import annotations

import sys
from pathlib import Path

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.window import Window

from src.transforms.transform_to_silver import load_cfg, build_spark

def read_silver_for_date(spark: SparkSession, date: str):
    base = Path("data/silver") / date
    path_glob = str(base / "*" / "*.parquet")  # data/silver/<date>/<category>/*.parquet
    return spark.read.parquet(path_glob)

def compute_daily(df):
    # Assumes df has: ticker, category, date (DATE), datetime (ts), open/high/low/close/volume
    # Window per ticker/day ordered by time for first/last
    w_day = Window.partitionBy("ticker", "category", "date").orderBy(F.col("datetime").asc())
    w_day_desc = Window.partitionBy("ticker", "category", "date").orderBy(F.col("datetime").desc())

    first_row = df.withColumn("rn_open", F.row_number().over(w_day)) \
                  .where(F.col("rn_open") == 1) \
                  .select("ticker", "category", "date", F.col("open").alias("open"))

    last_row = df.withColumn("rn_close", F.row_number().over(w_day_desc)) \
                 .where(F.col("rn_close") == 1) \
                 .select("ticker", "category", "date", F.col("close").alias("close"))

    agg = (df.groupBy("ticker", "category", "date")
             .agg(F.max("high").alias("high"),
                  F.min("low").alias("low"),
                  F.sum("volume").alias("volume")))

    daily = (agg.join(first_row, ["ticker", "category", "date"], "left")
                .join(last_row, ["ticker", "category", "date"], "left"))

    # daily return by ticker (order by date)
    w_ticker = Window.partitionBy("ticker").orderBy(F.col("date").asc())
    daily = daily.withColumn("prev_close", F.lag("close").over(w_ticker)) \
                 .withColumn("daily_return", F.when(F.col("prev_close").isNull(), None)
                                           .otherwise((F.col("close") / F.col("prev_close")) - 1)) \
                 .drop("prev_close")
    return daily

def delete_existing_date_in_pg(spark, cfg, date: str):
    # Idempotency: remove existing rows for this date, then append fresh ones.
    # Use Spark's JDBC to run a simple DELETE.
    url  = cfg.get("jdbc_url", "jdbc:postgresql://postgres:5432/yfinance")
    user = cfg.get("jdbc_user", "yfinance_app")
    pwd  = cfg.get("jdbc_password", "password")

    # Spark can't run arbitrary SQL via JDBC writer, so use a tiny driver-side call.
    # We'll leverage a one-row DataFrame and Postgres 'delete where' by pushing a query.
    # Easiest path: use psycopg2 if available (it is in your requirements).
    import psycopg2
    conn = psycopg2.connect(host=url.split("//")[1].split(":")[0],
                            port=int(url.split(":")[-1].split("/")[0]),
                            dbname=url.split("/")[-1],
                            user=user, password=pwd)
    cur = conn.cursor()
    cur.execute("DELETE FROM public.gold_daily_ohlc WHERE date = %s;", (date.replace("_", "-"),))
    conn.commit()
    cur.close()
    conn.close()

def write_daily_to_pg(daily_df, cfg):
    url  = cfg.get("jdbc_url", "jdbc:postgresql://postgres:5432/yfinance")
    user = cfg.get("jdbc_user", "yfinance_app")
    pwd  = cfg.get("jdbc_password", "password")

    (daily_df
        .select("ticker", "category", "date", "open", "high", "low", "close", "volume", "daily_return")
        .write
        .mode("append")
        .format("jdbc")
        .option("url", url)
        .option("dbtable", "public.gold_daily_ohlc")
        .option("user", user)
        .option("password", pwd)
        .option("driver", "org.postgresql.Driver")
        .save())

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.transforms.silver_to_gold <YYYY_MM_DD>")
        sys.exit(1)

    date = sys.argv[1]  # e.g., 2025_10_06

    cfg = load_cfg()
    spark = build_spark(cfg)

    # Read Silver for the date
    df = read_silver_for_date(spark, date)

    # Compute daily aggregates
    daily = compute_daily(df)

    # Idempotent write
    delete_existing_date_in_pg(spark, cfg, date)
    write_daily_to_pg(daily, cfg)

    # quick count
    print(f"[GOLD] wrote {daily.count()} rows for {date}")

    spark.stop()

if __name__ == "__main__":
    main()
