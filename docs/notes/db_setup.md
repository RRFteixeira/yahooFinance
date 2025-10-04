# Postgres (Docker) Setup

## 1) Prereqs
- Docker Desktop (or Docker Engine) installed and running.

## 2) Bring up the database

"bash"
cp .env          
docker compose -f docker/compose.db.yml up -d
docker ps
docker logs -f yfinance-postgres


## 3) run db database

docker exec -it yfinance-postgres psql -U yfinance_app -d yfinance

\q 