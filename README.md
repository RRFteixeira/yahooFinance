# 📈 Yahoo Finance Data Engineering Pipeline

An end-to-end data engineering project built with free tools to ingest, process, and store financial market data from Yahoo Finance.  
The pipeline supports both **batch ETL** and **streaming ingestion** via Apache Kafka, showcasing scalable and modern data engineering practices.

---

## ⚠️ Disclaimer
This project is a **work in progress** and is still under active development.  

It was **partially developed with the assistance of AI tools** to accelerate learning, design, and implementation.  
The main purpose of this repository is to **practice data engineering skills**, showcase a modern stack, and document my learning journey.


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

## ✅ Batch vs Streaming

### 📦 Batch Mode (ETL)
- Triggered daily with **Airflow**  
- Fetches historical **1-min stock bars**  
- Processes with **PySpark**  
- Stores results in **Parquet**

### ⚡ Streaming Mode (Kafka)
- `kafka_producer.py` pushes stock ticks (simulated or via yfinance polling)  
- `kafka_consumer.py` consumes events and writes to **Bronze (raw) storage**  
- Later transformations (**Silver/Gold layers**) handled in **Spark**

---

## 🗺️ Roadmap
- **Phase 0:** Repo scaffolding, Docker stack. 
- **Phase 1:** Batch ingestion with Airflow + pandas. 
- **Phase 2:** Transformations in PySpark. 
- **Phase 3:** Add Kafka producer/consumer for real-time ingestion. 
- **Phase 4:** Data quality checks (Great Expectations). 
- **Phase 5:** Cloud-ready infra with Terraform + AWS S3. 

---

## 🙋‍♂️ What I Learned
- Orchestration with **Airflow** vs event-driven streaming with **Kafka**  
- Designing **idempotent batch jobs** and **at-least-once streaming consumers**  
- Balancing **pandas for prototyping** vs **PySpark for scale**  
- Structuring a **`src/` project layout** for clean imports and testing  

---
