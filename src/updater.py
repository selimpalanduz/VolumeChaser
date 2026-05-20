import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime,timedelta

DATA_DIR=Path(__file__).parent.parent / "data"
TICKERS_PATH=DATA_DIR / "tickers.txt"
CACHE_PATH=DATA_DIR / "cache.parquet"

def load_tickers():
    if not TICKERS_PATH.exists():
        raise FileNotFoundError(f"{TICKERS_PATH} not found")
    with open(TICKERS_PATH,"r",encoding="utf-8") as f:
        tickers = [line.strip() for line in f if line.strip()]
    return tickers

def fetch_stock(symbol, days=200):
    """Fetch OHLCV data for a single BIST stock from yfinance."""
    end = datetime.today()
    start = end - timedelta(days=days)
    stock = yf.Ticker(f"{symbol}.IS")
    data = stock.history(start=start, end=end)
    data["Symbol"] = symbol
    return data

def update_cache(days=200):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    symbols = load_tickers()
    print(f"Loaded {len(symbols)} tickers from {TICKERS_PATH.name}\n")

    all_data = []
    failed=[]
    for i, symbol in enumerate(symbols, 1):
        print(f"[{i}/{len(symbols)}] Fetching {symbol}...")
        try:
            data = fetch_stock(symbol, days=days)
            if not data.empty:
                all_data.append(data)
            else:
                failed.append(symbol)
        except Exception as e:
            print(f"  Error: {e}")
            failed.append(symbol)
    
    combined = pd.concat(all_data)
    combined.to_parquet(CACHE_PATH)
    
    print(f"\nCache saved to {CACHE_PATH}")
    print(f"Total rows: {len(combined)} | Symbols: {combined['Symbol'].nunique()}")
    if failed:
        print(f"Failed ({len(failed)}): {', '.join(failed)}")


if __name__ == "__main__":
    update_cache()
