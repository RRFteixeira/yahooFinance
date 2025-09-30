import yfinance as yf
import json
from pathlib import Path
import os
import datetime
import logging

def fetch_all_tickers(path: str):
    dir_list = os.listdir(path=path)
    
    for dir in dir_list:
        ticker_path = path + dir
        fetch_ticker(file_path=ticker_path) 

def fetch_ticker(file_path: str):
    
    sysdate = datetime.datetime.today().strftime('%Y_%m_%d')
    
    # Configure logging
    logging.basicConfig(
        filename=f"data/raw/{sysdate}/yfinance_error.log",
        level=logging.INFO,          
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    with open(file=file_path) as f:
        tickers = json.load(fp=f)
        ticker_category= file_path.removeprefix('stocks/').removesuffix('.json')
        
            
        for ticker in tickers.keys():
       
            print(f'Downloading ticker: {sysdate}/{ticker_category}/{ticker}')
            
            data = yf.download(tickers=ticker, multi_level_index=False, auto_adjust=False, interval="1m", period="7d")
            data = data.reset_index()
            out_dir = Path(f"data/raw/{sysdate}/{ticker_category}/")
            out_dir.mkdir(parents=True, exist_ok= True, )
            out_path = out_dir / f"{ticker}.parquet"
            data.to_parquet(path=out_path, index=False, engine="pyarrow", compression="snappy")           

if __name__ == '__main__':
    fetch_all_tickers(path='stocks/')
