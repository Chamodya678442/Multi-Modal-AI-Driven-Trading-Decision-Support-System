import numpy as np
import pandas as pd


def calculate_sma(series: pd.Series, period: int) -> pd.Series:
    """Calculates Simple Moving Average (SMA)."""
    return series.rolling(window=period).mean()


def calculate_ma_crossover(sma_short: pd.Series, sma_long: pd.Series) -> pd.Series:
    """
    Detects Moving Average Crossover events:
    +1: Bullish Crossover (Golden Cross: short MA crosses above long MA)
    -1: Bearish Crossover (Death Cross: short MA crosses below long MA)
     0: No crossover event
    """
    signal = pd.Series(0, index=sma_short.index, dtype=int)
    
    # Previous period comparison to detect crossing moment
    bullish = (sma_short > sma_long) & (sma_short.shift(1) <= sma_long.shift(1))
    bearish = (sma_short < sma_long) & (sma_short.shift(1) >= sma_long.shift(1))
    
    signal[bullish] = 1
    signal[bearish] = -1
    return signal


def calculate_bollinger_bands(series: pd.Series, period: int = 20, std_dev: float = 2.0):
    """
    Calculates Bollinger Bands:
    - Middle Band: 20-period SMA
    - Upper Band: Middle Band + 2 * standard deviation
    - Lower Band: Middle Band - 2 * standard deviation
    """
    middle = series.rolling(window=period).mean()
    rolling_std = series.rolling(window=period).std()
    upper = middle + (std_dev * rolling_std)
    lower = middle - (std_dev * rolling_std)
    return upper, middle, lower


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculates Average True Range (ATR) using Wilder's smoothing.
    TR = max(High - Low, abs(High - Close_prev), abs(Low - Close_prev))
    """
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # Wilder's exponential smoothing (alpha = 1 / period)
    atr = true_range.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    return atr


def calculate_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculates Relative Strength Index (RSI, 14-period).
    RS = Average Gain / Average Loss
    RSI = 100 - (100 / (1 + RS))
    """
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    # Exponential Wilder smoothing
    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    # Handle zero loss edge-case (RSI = 100)
    rsi = rsi.fillna(100.0)
    return rsi


def calculate_macd(
    close: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
):
    """
    Calculates MACD (12, 26, 9):
    - MACD Line = EMA(12) - EMA(26)
    - Signal Line = EMA(9) of MACD Line
    - Histogram = MACD Line - Signal Line
    """
    ema_fast = close.ewm(span=fast_period, adjust=False).mean()
    ema_slow = close.ewm(span=slow_period, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def compute_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes all technical indicators defined in project proposal:
    SMA 20, SMA 50, MA Crossover, Bollinger Bands (20, 2), ATR (14), RSI (14), MACD (12, 26, 9).
    Expects df with columns: ['open', 'high', 'low', 'close', 'volume'].
    """
    result = pd.DataFrame(index=df.index)
    
    # Moving Averages & Crossover
    result["sma_20"] = calculate_sma(df["close"], period=20)
    result["sma_50"] = calculate_sma(df["close"], period=50)
    result["ma_crossover"] = calculate_ma_crossover(result["sma_20"], result["sma_50"])
    
    # Bollinger Bands
    result["bb_upper"], result["bb_middle"], result["bb_lower"] = calculate_bollinger_bands(
        df["close"], period=20, std_dev=2.0
    )
    
    # ATR (Volatility)
    result["atr_14"] = calculate_atr(df["high"], df["low"], df["close"], period=14)
    
    # RSI (Momentum)
    result["rsi_14"] = calculate_rsi(df["close"], period=14)
    
    # MACD (Trend & Momentum)
    result["macd"], result["macd_signal"], result["macd_hist"] = calculate_macd(
        df["close"], fast_period=12, slow_period=26, signal_period=9
    )
    
    return result
