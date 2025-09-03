from datetime import date, timedelta
import pandas as pd
import argparse
import yfinance as yf
from pathlib import Path

def fetch_prices(tickerStrings: list = ['AAPL','MSFT'], days: int = 30) -> Path:
    

    
    end = date.today()
    start = end - timedelta(days=days)



    for ticker in tickerStrings:
        data = yf.download(ticker, multi_level_index=False, auto_adjust=False, interval="1m", period="7d")
        data['ticker'] = ticker  # Add ticker column
        
        data = data.reset_index()
        print(data.head())
        print(data.columns)
        out_dir = Path("data")
        out_dir.mkdir(parents=True, exist_ok= True, )
        out_path = out_dir / f"{ticker}_prices.parquet"
        data.to_parquet(path=out_path, index=False, engine="pyarrow", compression="snappy")

if __name__ == '__main__':
    p = fetch_prices()
    print(f"saved: {p}")
