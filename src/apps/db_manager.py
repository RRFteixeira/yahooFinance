import os
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def _db_url() -> str:
    user = os.getenv("POSTGRES_USER", "yfinance_app")
    pwd  = os.getenv("POSTGRES_PASSWORD", "password")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5433")
    db   = os.getenv("POSTGRES_DB", "yfinance")
    return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"

ENGINE = create_engine(_db_url(), pool_pre_ping=True, future=True)

@contextmanager
def db_conn():
    with ENGINE.begin() as conn:
        yield conn

def log_ingestion(
    *,
    ticker: str,
    file_path: str,
    status: str,
    category: Optional[str] = None,
    rows_written: Optional[int] = None,
    error_message: Optional[str] = None,
    run_ts_utc: Optional[datetime] = None,
) -> None:
    run_ts = run_ts_utc or datetime.now(timezone.utc)
    stmt = text("""
        INSERT INTO meta.ingestions
          (run_ts_utc, ticker, category, file_path, status, rows_written, error_message)
        VALUES
          (:run_ts_utc, :ticker, :category, :file_path, :status, :rows_written, :error_message)
    """)
    with db_conn() as conn:
        conn.execute(stmt, {
            "run_ts_utc": run_ts,
            "ticker": ticker,
            "category": category,
            "file_path": file_path,
            "status": status,
            "rows_written": rows_written,
            "error_message": error_message,
        })

def smoke_check() -> bool:
    with db_conn() as conn:
        conn.execute(text("SELECT 1"))
    return True

if __name__ == "__main__":
    print("DB URL:", _db_url())
    print("Smoke:", smoke_check())
