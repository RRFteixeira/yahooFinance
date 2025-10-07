from src.apps.db_manager import log_ingestion

from pathlib import Path
import yfinance as yf
import json
import os
import datetime
import logging
import pandas as pd

def fetch_all_tickers(path: str):
    dir_list = os.listdir(path=path)
    
    for dir in dir_list:
        ticker_path = path + dir
        fetch_ticker(file_path=ticker_path) 

def fetch_ticker(file_path: str):
    
    sysdate = datetime.datetime.today().strftime('%Y_%m_%d')
    log_dir = Path(f"data/bronze/{sysdate}")
    log_dir.mkdir(parents=True, exist_ok=True)    
    # Configure logging
    logging.basicConfig(
        filename=f"data/bronze/{sysdate}/yfinance_error.log",
        level=logging.INFO,          
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    with open(file=file_path) as f:
        tickers = json.load(fp=f)
        ticker_category= file_path.removeprefix('stocks/').removesuffix('.json')
        
            
        for ticker in tickers.keys():
            
            print(f'Downloading ticker: {sysdate}/{ticker_category}/{ticker}')
            out_dir = Path(f"data/bronze/{sysdate}/{ticker_category}/")
            out_dir.mkdir(parents=True, exist_ok= True, )
            out_path = out_dir / f"{ticker}.parquet"
            

            data = yf.download(tickers=ticker, multi_level_index=False, auto_adjust=False, interval="1m", period="7d")
            data = data.reset_index()
            data.to_parquet(path=out_path, index=False, engine="pyarrow", compression="snappy", coerce_timestamps="us", allow_truncated_timestamps=True)

            
            if len(data)<200:
                err_msg = f"{ticker}: invalid number of rows. row: {len(data)}"
                log_ingestion(ticker=ticker, file_path=str(out_path), status="FAILED", category=ticker_category, rows_written=len(data), error_message=err_msg)

            else:
                log_ingestion(ticker=ticker, file_path=str(out_path), status="SUCCESS", category=ticker_category, rows_written=len(data))

                      

if __name__ == '__main__':
    fetch_all_tickers(path='stocks/')
