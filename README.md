# 📈 Yahoo Finance Data Engineering Pipeline

An end-to-end data engineering project built with free tools to ingest, process, and store financial market data from Yahoo Finance.  
The pipeline supports both **batch ETL** and **streaming ingestion** via Apache Kafka, showcasing scalable and modern data engineering practices.

---

## 🎯 Objectives
- Build a **daily batch ETL pipeline** with Airflow, PySpark, and Parquet.
- Extend with **real-time ingestion** of stock ticks through Kafka.
- Demonstrate **scalability** from 100 → 1000+ tickers.
- Showcase both **data engineering skills** and a clear **learning journey**.

---

## 🔧 Tech Stack
- **Python 3.x** – core ETL and utilities.
- **Apache Airflow** – batch orchestration & scheduling.
- **Apache Kafka** – streaming ingestion and message queue.
- **PySpark** – distributed processing of large datasets.
- **Pandas** – lightweight transforms & exploration.
- **Docker Compose** – reproducible local dev stack (Airflow + Kafka + MinIO).
- **MinIO / Local FS** – object storage (S3-compatible).
- **GitHub Actions** – CI for linting & testing.
- **Parquet** – columnar storage format.

---

## 🧠 Why These Technologies?
- **Airflow** → robust batch scheduling, retries, DAG-based orchestration.  
- **Kafka** → real-time streaming of stock events into the pipeline.  
- **PySpark** → distributed processing when scaling beyond pandas.  
- **Parquet** → compressed, analytical storage.  
- **Docker** → unified stack with Airflow, Kafka, and Spark.  
- **GitHub Actions** → free CI automation for public repos.  

---
