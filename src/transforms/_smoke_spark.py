from pyspark.sql import SparkSession

def main():
    spark = (
        SparkSession.builder
        .appName("yahoo-smoke")
        .master("local[2]")
        .config("spark.driver.host", "127.0.0.1")      # <-- key
        .config("spark.driver.bindAddress", "127.0.0.1")  # <-- key
        .config("spark.sql.shuffle.partitions", 4)
        .getOrCreate()
    )
    print("Spark range(5) →")
    print(spark.range(5).toPandas())
    spark.stop()
    print("Spark stopped cleanly.")

if __name__ == "__main__":
    main()
