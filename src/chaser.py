import pandas as pd
from pathlib import Path


CACHE_PATH = Path(__file__).parent.parent / "data" / "cache.parquet"


def load_cache():
    """Load OHLCV data from parquet cache."""
    if not CACHE_PATH.exists():
        raise FileNotFoundError(
            f"No cache found at {CACHE_PATH}. Run updater.py first."
        )
    return pd.read_parquet(CACHE_PATH)


def add_rvol(data, window=20):
    """Add Relative Volume column."""
    data = data.copy()
    data["AvgVolume"] = data["Volume"].rolling(window=window).mean()
    data["RVOL"] = data["Volume"] / data["AvgVolume"]
    return data


def scan(window=20):
    """Compute RVOL for all symbols, return last completed day sorted by RVOL."""
    df = load_cache()
    results = []
    
    for symbol, group in df.groupby("Symbol"):
        group = group.sort_index()
        group = add_rvol(group, window=window)
        last = group.iloc[-2]  # skip today (incomplete bar)
        results.append({
            "Symbol": symbol,
            "Date": last.name.date(),
            "Close": round(last["Close"], 2),
            "Volume": int(last["Volume"]),
            "RVOL": round(last["RVOL"], 2),
        })
    
    return pd.DataFrame(results).sort_values("RVOL", ascending=False)


if __name__ == "__main__":
    df = scan()
    
    # Sadece RVOL > 1.5 olanları göster (anomali olanlar)
    print("=== Anomaly candidates (RVOL > 1.5) ===")
    print(df[df["RVOL"] > 1.5].to_string(index=False))
    
    print(f"\nTotal symbols scanned: {len(df)}")