# Yahoo Finance Data Engineering Pipeline

An end-to-end data engineering project built with free tools to ingest, process, and store financial market data from Yahoo Finance.  
The pipeline supports both **batch ETL** and **streaming ingestion** via Apache Kafka, showcasing scalable and modern data engineering practices.

---

## ⚠️ Disclaimer
This project is a **work in progress** and is still under active development.  

It was **partially developed with the assistance of AI tools** to accelerate learning, design, and implementation.  
The main purpose of this repository is to **practice data engineering skills**, showcase a modern stack, and document my learning journey.


---

## Objectives
- Build a **daily batch ETL pipeline** with Airflow, PySpark, and Parquet.
- Extend with **real-time ingestion** of stock ticks through Kafka.
- Demonstrate **scalability** from 100 → 1000+ tickers.
- Showcase both **data engineering skills** and a clear **learning journey**.

---

## Tech Stack
- **Python** – core ETL logic and utilities  
- **Apache Airflow** – batch orchestration and scheduling  
- **Apache Kafka** – streaming ingestion and event delivery  
- **PySpark** – distributed processing for large datasets  
- **Pandas** – lightweight transformations and exploration  
- **Docker Compose** – reproducible local environment (Airflow, Kafka, MinIO)  
- **MinIO** – S3-compatible object storage  
- **Parquet** – efficient columnar storage format  
- **Delta Tables** – ACID storage layer on top of Parquet  
- **Terraform** – infrastructure as code (for future cloud deployment)  
- **GitHub Actions** – CI for testing and linting  

---

## Why These Technologies?

- **Airflow** – production-grade scheduler with retries and monitoring  
- **Kafka** – handles real-time data streams  
- **PySpark** – scales transformations beyond pandas limits  
- **Parquet** – compact and optimized for analytics  
- **Delta Tables** – provides versioning and transactional reliability  
- **Docker** – consistent local stack for all services  
- **MinIO** – self-hosted object storage compatible with AWS S3  
- **Terraform** – automates infrastructure setup and provisioning  
- **GitHub Actions** – continuous integration and automation  

Everything is free, runs locally, and mirrors real-world data engineering patterns.

---

## Roadmap
- **Phase 0:** Project setup and repository structure  
- **Phase 1:** Initial Yahoo Finance data extraction  
- **Phase 2:** Store data in Parquet (Bronze layer)  
- **Phase 3:** Metadata logging in PostgreSQL  
- **Phase 4:** Error handling and logging system  
- **Phase 5:** Modularization and configuration management  
- **Phase 6:** Airflow integration and automated ingestion (current phase)  
- **Phase 7:** Add MinIO and Delta Lake for object storage  
- **Phase 8:** Introduce PySpark for Silver/Gold transformations  
- **Phase 9:** Kafka streaming ingestion  
- **Phase 10:** Infrastructure with Terraform and CI/CD pipeline  


## How to start
**1** - docker network create yf_net
**2** - docker compose -f docker/compose.db.yml up -d
**3** - docker compose -f docker/compose.airflow.yml up -d
**4** - docker compose -f docker/compose.airflow.yml up -d
**4** - http://localhost:8080 Username: admin Password: admin
**5** - stop everything - docker compose -f docker/compose.airflow.yml down docker compose -f docker/compose.db.yml down


---


