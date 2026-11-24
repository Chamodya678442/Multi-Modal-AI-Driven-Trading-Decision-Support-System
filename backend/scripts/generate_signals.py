import sys
import time
from pathlib import Path
import pandas as pd

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.db.session import engine
from app.services.signals import generate_baseline_signals


def run_signals_pipeline():
    print("=== TRADING SIGNAL GENERATION PIPELINE ===")

    with engine.connect() as conn:
        # 1. Fetch joined candle & indicator data
        print("Fetching candles and indicators from PostgreSQL...")
        query = text("""
            SELECT c.id AS candle_id, c.open_time, c.close,
                   i.sma_20, i.sma_50, i.ma_crossover,
                   i.bb_upper, i.bb_middle, i.bb_lower,
                   i.atr_14, i.rsi_14, i.macd_hist
            FROM market_candles c
            JOIN technical_indicators i ON c.id = i.candle_id
            ORDER BY c.open_time ASC;
        """)
        df = pd.read_sql(query, conn)
        print(f"Loaded {len(df):,} records for signal analysis.")

        if len(df) == 0:
            print("Error: No data found. Please run calculate_indicators.py first.")
            return

        # 2. Check if signals table already has records
        count = conn.execute(text("SELECT COUNT(*) FROM trading_signals;")).scalar()
        if count and count > 0:
            print(f"Notice: 'trading_signals' table already contains {count:,} records.")
            choice = input("Do you want to re-generate and overwrite existing signals? (y/N): ")
            if choice.lower() == "y":
                print("Clearing table 'trading_signals'...")
                conn.execute(text("TRUNCATE TABLE trading_signals RESTART IDENTITY;"))
                conn.commit()
            else:
                print("Skipping signal generation.")
                return

    # 3. Generate signals with explanations
    print("Evaluating rules: MA Crossover, Bollinger Bands, RSI & ATR Risk Filter...")
    start_time = time.time()
    signals_df = generate_baseline_signals(df)
    signals_df["candle_id"] = df["candle_id"]

    calc_elapsed = time.time() - start_time
    print(f"Signals generated in {calc_elapsed:.2f} seconds.")

    # 4. Bulk insert into PostgreSQL
    print(f"Inserting {len(signals_df):,} signals into 'trading_signals' table...")
    insert_start = time.time()
    signals_df.to_sql(
        name="trading_signals",
        con=engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=2000
    )
    insert_elapsed = time.time() - insert_start
    print(f"Successfully inserted signals in {insert_elapsed:.2f} seconds!")

    # 5. Summary & Verification
    with engine.connect() as conn:
        counts = pd.read_sql(
            text("SELECT signal, COUNT(*) as count FROM trading_signals GROUP BY signal ORDER BY count DESC;"),
            conn
        )
        print("\n--- SIGNAL DISTRIBUTION SUMMARY ---")
        print(counts.to_string(index=False))

        # Sample BUY signals
        sample_buy = pd.read_sql(text("""
            SELECT c.open_time, c.close, s.signal, s.reason
            FROM trading_signals s
            JOIN market_candles c ON s.candle_id = c.id
            WHERE s.signal = 'BUY'
            LIMIT 3;
        """), conn)
        print("\nSample Generated BUY Signals with Explanations:")
        print(sample_buy.to_string(index=False))


if __name__ == "__main__":
    run_signals_pipeline()
