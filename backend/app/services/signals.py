import pandas as pd


def generate_baseline_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates rule-based BUY, SELL, and HOLD recommendations with transparent explanations.
    Combines Moving Average Crossover, Bollinger Bands, RSI, and ATR volatility checks.
    
    Expects df with columns:
    ['close', 'sma_20', 'sma_50', 'ma_crossover', 'bb_upper', 'bb_middle', 'bb_lower', 'atr_14', 'rsi_14', 'macd_hist']
    """
    signals = []
    reasons = []
    
    # Dynamic ATR baseline (rolling 100-period average ATR) for volatility threshold
    rolling_atr_mean = df["atr_14"].rolling(window=100, min_periods=20).mean()

    for idx, row in df.iterrows():
        # During initial warmup periods when indicators are NaN, output HOLD
        if pd.isna(row["sma_50"]) or pd.isna(row["bb_lower"]) or pd.isna(row["rsi_14"]) or pd.isna(row["atr_14"]):
            signals.append("HOLD")
            reasons.append("Insufficient historical periods for indicator calculation (warmup phase).")
            continue

        close = row["close"]
        sma_20 = row["sma_20"]
        sma_50 = row["sma_50"]
        crossover = row["ma_crossover"]
        bb_upper = row["bb_upper"]
        bb_lower = row["bb_lower"]
        rsi = row["rsi_14"]
        atr = row["atr_14"]
        macd_hist = row.get("macd_hist", 0)
        atr_avg = rolling_atr_mean.loc[idx] if not pd.isna(rolling_atr_mean.loc[idx]) else atr

        # Volatility assessment: reject entry if ATR is abnormally elevated (> 2.0x average)
        is_high_volatility = atr > (1.8 * atr_avg)

        # 1. BUY Condition
        bullish_ma = (crossover == 1) or (sma_20 > sma_50 and close > sma_20)
        oversold_bb = close <= (bb_lower * 1.01)
        healthy_rsi = rsi < 48
        
        if (bullish_ma or oversold_bb) and healthy_rsi:
            if is_high_volatility:
                signals.append("HOLD")
                reasons.append(
                    f"Risk Filter: Bullish conditions present, but ATR volatility ({atr:.2f}) "
                    f"exceeds safety threshold (1.8x avg: {1.8 * atr_avg:.2f}). Recommendation clamped to HOLD."
                )
            else:
                signals.append("BUY")
                reasons.append(
                    f"BUY Confirmed: {'Golden Cross' if crossover == 1 else 'SMA20 > SMA50'} with "
                    f"RSI at {rsi:.1f} and price near lower Bollinger Band."
                )
            continue

        # 2. SELL Condition
        bearish_ma = (crossover == -1) or (sma_20 < sma_50 and close < sma_20)
        overbought_bb = close >= (bb_upper * 0.99)
        overbought_rsi = rsi > 65

        if (bearish_ma or overbought_bb) and overbought_rsi:
            signals.append("SELL")
            reasons.append(
                f"SELL Confirmed: {'Death Cross' if crossover == -1 else 'SMA20 < SMA50'} with "
                f"RSI overbought at {rsi:.1f} and price touching upper Bollinger Band ({bb_upper:.2f})."
            )
            continue

        # 3. Default: HOLD
        signals.append("HOLD")
        if is_high_volatility:
            reasons.append(
                f"HOLD: Elevated market volatility detected (ATR: {atr:.2f}). Awaiting market stabilization."
            )
        else:
            reasons.append(
                f"HOLD: Market in consolidation. Trend neutral (SMA20: {sma_20:.2f}, SMA50: {sma_50:.2f}), RSI neutral at {rsi:.1f}."
            )

    result_df = pd.DataFrame({
        "signal": signals,
        "strategy": "Technical_Rule_Based_V1",
        "reason": reasons
    }, index=df.index)

    return result_df
