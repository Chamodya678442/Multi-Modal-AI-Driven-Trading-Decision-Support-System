import sys
import time
from pathlib import Path
import pandas as pd

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.db.session import engine


def ingest_candles():
    project_root = backend_dir.parent
    csv_file = project_root / "data" / "BTCUSDT_15m_1year.csv"

    if not csv_file.exists():
        print(f"Error: CSV file not found at {csv_file}")
        sys.exit(1)

    print(f"Reading dataset: {csv_file}")
    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df):,} records from CSV.")

    # Check existing records in database to avoid duplicate key errors
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM market_candles;")).scalar()
        if count and count > 0:
            print(f"Warning: 'market_candles' table already contains {count:,} records.")
            response = input("Do you want to clear the table and re-ingest? (y/N): ")
            if response.lower() == "y":
                print("Clearing table 'market_candles'...")
                conn.execute(text("TRUNCATE TABLE market_candles RESTART IDENTITY CASCADE;"))
                conn.commit()
            else:
                print("Skipping ingestion.")
                return

    print("Formatting timestamps and columns for PostgreSQL schema...")
    df["open_time"] = pd.to_datetime(df["Open_Time"], unit="us", utc=True)
    df["close_time"] = pd.to_datetime(df["Close_Time"], unit="us", utc=True)

    # Rename to match PostgreSQL model column names
    rename_mapping = {
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
        "Quote_Volume": "quote_volume",
        "Number_of_Trades": "trades_count",
        "Taker_Buy_Base": "taker_buy_base",
        "Taker_Buy_Quote": "taker_buy_quote",
    }
    df = df.rename(columns=rename_mapping)

    df["symbol"] = "BTCUSDT"
    df["timeframe"] = "15m"

    target_columns = [
        "symbol",
        "timeframe",
        "open_time",
        "close_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quote_volume",
        "trades_count",
        "taker_buy_base",
        "taker_buy_quote",
    ]

    df_to_insert = df[target_columns]

    print(f"Starting bulk insert of {len(df_to_insert):,} candles into PostgreSQL...")
    start_time = time.time()

    # Fast multi-row insertion with chunksize
    df_to_insert.to_sql(
        name="market_candles",
        con=engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=2000,
    )

    elapsed = time.time() - start_time
    print(f"Successfully ingested {len(df_to_insert):,} candles in {elapsed:.2f} seconds!")

    # Verify count
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM market_candles;")).scalar()
        print(f"Verification: Total records in 'market_candles' table = {total:,}")


if __name__ == "__main__":
    print("=== INGESTING CANDLESTICK DATA INTO POSTGRESQL ===")
    ingest_candles()
    print("=== INGESTION FINISHED ===")
