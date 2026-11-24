import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.services.indicators import (
    calculate_sma,
    calculate_ma_crossover,
    calculate_bollinger_bands,
    calculate_atr,
    calculate_rsi,
    calculate_macd,
    compute_all_indicators
)


def test_indicators_math():
    print("Testing technical indicators calculations...")
    
    # Generate mock 100 periods of sample price data
    np.random.seed(42)
    closes = 50000 + np.cumsum(np.random.randn(100) * 100)
    highs = closes + np.random.rand(100) * 50
    lows = closes - np.random.rand(100) * 50
    opens = closes + np.random.randn(100) * 20
    volumes = np.random.rand(100) * 10
    
    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes
    })
    
    indicators = compute_all_indicators(df)
    
    # 1. Check SMA
    assert "sma_20" in indicators.columns
    assert "sma_50" in indicators.columns
    assert np.isnan(indicators["sma_20"].iloc[0])  # first 19 should be NaN
    assert not np.isnan(indicators["sma_20"].iloc[19])  # 20th should be valid
    
    # 2. Check Bollinger Bands
    assert (indicators["bb_upper"].dropna() >= indicators["bb_middle"].dropna()).all()
    assert (indicators["bb_middle"].dropna() >= indicators["bb_lower"].dropna()).all()
    
    # 3. Check ATR
    assert (indicators["atr_14"].dropna() > 0).all()
    
    # 4. Check RSI bounds (0 <= RSI <= 100)
    valid_rsi = indicators["rsi_14"].dropna()
    assert (valid_rsi >= 0).all() and (valid_rsi <= 100).all()
    
    # 5. Check MACD Histogram = MACD - Signal
    valid_macd = indicators.dropna()
    diff = (valid_macd["macd"] - valid_macd["macd_signal"]) - valid_macd["macd_hist"]
    assert np.allclose(diff, 0, atol=1e-5)
    
    print("All indicator mathematical checks PASSED successfully!")


if __name__ == "__main__":
    test_indicators_math()
