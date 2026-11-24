import sys
from pathlib import Path
import pandas as pd

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.db.session import engine


def verify_database():
    print("=== POSTGRESQL DATABASE VERIFICATION ===")

    try:
        with engine.connect() as conn:
            # 1. Check connection
            version = conn.execute(text("SELECT version();")).scalar()
            print(f"Connected to: {version}\n")

            # 2. Check table row counts
            for table in ["market_candles", "technical_indicators", "trading_signals"]:
                try:
                    count = conn.execute(text(f"SELECT COUNT(*) FROM {table};")).scalar()
                    print(f"Table '{table}': {count:,} records")
                except Exception as e:
                    print(f"Table '{table}': Not found or error: {e}")

            # 3. Query sample records from market_candles
            print("\nFirst 3 candles in database:")
            sample_df = pd.read_sql(
                text("SELECT id, symbol, open_time, open, high, low, close, volume FROM market_candles ORDER BY open_time ASC LIMIT 3;"),
                conn
            )
            print(sample_df.to_string(index=False))

            print("\nLast 3 candles in database:")
            sample_last_df = pd.read_sql(
                text("SELECT id, symbol, open_time, open, high, low, close, volume FROM market_candles ORDER BY open_time DESC LIMIT 3;"),
                conn
            )
            print(sample_last_df.to_string(index=False))

    except Exception as e:
        print(f"Connection failed: {e}")


if __name__ == "__main__":
    verify_database()
