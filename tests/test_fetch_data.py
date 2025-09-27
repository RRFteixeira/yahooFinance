from src.apps.fetch_data import fetch_prices
from pathlib import Path

def test_fetch_prices_creates_file(tmp_path, monkeypatch):
    # redirect output folder to tmp_path
    def fake_mkdir(**kwargs): pass
    p = fetch_prices("AAPL", 5)
    assert Path(p).exists()