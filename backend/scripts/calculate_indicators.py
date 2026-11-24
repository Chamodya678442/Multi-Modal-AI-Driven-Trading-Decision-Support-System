import sys
import time
from pathlib import Path
import pandas as pd

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.db.session import engine
from app.services.indicators import compute_all_indicators


def run_indicator_pipeline():
    print("=== TECHNICAL ANALYSIS INDICATOR PIPELINE ===")
    
    with engine.connect() as conn:
        # 1. Fetch candles from database
        print("Fetching market candles from PostgreSQL...")
        query = text(
            "SELECT id, open_time, open, high, low, close, volume "
            "FROM market_candles "
            "ORDER BY open_time ASC;"
        )
        df_candles = pd.read_sql(query, conn)
        print(f"Loaded {len(df_candles):,} candles from 'market_candles'.")

        if len(df_candles) == 0:
            print("Error: 'market_candles' table is empty. Please run ingest_candles.py first.")
            return

        # 2. Check if technical_indicators already has data
        count = conn.execute(text("SELECT COUNT(*) FROM technical_indicators;")).scalar()
        if count and count > 0:
            print(f"Warning: 'technical_indicators' table already contains {count:,} records.")
            choice = input("Do you want to re-compute and overwrite existing indicators? (y/N): ")
            if choice.lower() == "y":
                print("Clearing table 'technical_indicators'...")
                conn.execute(text("TRUNCATE TABLE technical_indicators RESTART IDENTITY;"))
                conn.commit()
            else:
                print("Skipping computation.")
                return

    # 3. Compute indicators
    print("Computing technical indicators (SMA 20/50, Crossover, Bollinger Bands, ATR, RSI, MACD)...")
    start_time = time.time()
    df_indicators = compute_all_indicators(df_candles)
    
    # Assign candle_id
    df_indicators["candle_id"] = df_candles["id"]
    
    # Ensure correct column ordering matching TechnicalIndicator model
    ordered_cols = [
        "candle_id",
        "sma_20",
        "sma_50",
        "ma_crossover",
        "bb_upper",
        "bb_middle",
        "bb_lower",
        "atr_14",
        "rsi_14",
        "macd",
        "macd_signal",
        "macd_hist"
    ]
    df_indicators = df_indicators[ordered_cols]
    
    calc_elapsed = time.time() - start_time
    print(f"Indicators computed in {calc_elapsed:.2f} seconds.")

    # 4. Bulk insert into PostgreSQL
    print(f"Inserting {len(df_indicators):,} indicator records into PostgreSQL...")
    insert_start = time.time()
    df_indicators.to_sql(
        name="technical_indicators",
        con=engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=2000
    )
    insert_elapsed = time.time() - insert_start
    print(f"Successfully inserted indicators in {insert_elapsed:.2f} seconds!")

    # 5. Verification & Summary
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM technical_indicators;")).scalar()
        crossovers = conn.execute(
            text("SELECT COUNT(*) FROM technical_indicators WHERE ma_crossover != 0;")
        ).scalar()
        print(f"\n--- VERIFICATION SUMMARY ---")
        print(f"Total indicator rows: {total:,}")
        print(f"Total MA Crossover events detected: {crossovers:,}")
        
        # Display sample record with open_time
        sample_query = text("""
            SELECT c.open_time, c.close, i.sma_20, i.sma_50, i.bb_upper, i.bb_lower, i.atr_14, i.rsi_14, i.macd
            FROM market_candles c
            JOIN technical_indicators i ON c.id = i.candle_id
            ORDER BY c.open_time DESC
            LIMIT 5;
        """)
        sample_df = pd.read_sql(sample_query, conn)
        print("\nLatest 5 candles with calculated indicators:")
        print(sample_df.to_string(index=False))


if __name__ == "__main__":
    run_indicator_pipeline()
