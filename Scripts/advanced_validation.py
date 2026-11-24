
import pandas as pd

FILE = "data/BTCUSDT_15m_1year.csv"

df = pd.read_csv(FILE)

# Convert timestamps from microseconds
df["Open_Time"] = pd.to_datetime(
    df["Open_Time"],
    unit="us",
    utc=True
)

df["Close_Time"] = pd.to_datetime(
    df["Close_Time"],
    unit="us",
    utc=True
)

df = df.sort_values("Open_Time").reset_index(drop=True)

# 1. Check 15-minute intervals
time_diff = df["Open_Time"].diff().dropna()

missing_intervals = (
    time_diff != pd.Timedelta(minutes=15)
).sum()

# 2. Validate OHLC relationships
invalid_high = (
    df["High"] < df[["Open", "Close", "Low"]].max(axis=1)
).sum()

invalid_low = (
    df["Low"] > df[["Open", "Close", "High"]].min(axis=1)
).sum()

# 3. Check invalid numerical values
invalid_prices = (
    (df[["Open", "High", "Low", "Close"]] <= 0)
    .any(axis=1)
).sum()

invalid_volume = (df["Volume"] < 0).sum()

# Binance candle duration in microsecond timestamps:
# 15 minutes minus 1 microsecond (899,999,999 us)
expected_duration = pd.Timedelta(
    minutes=15
) - pd.Timedelta(microseconds=1)

duration = (
    df["Close_Time"] - df["Open_Time"]
)

invalid_duration = (
    duration != expected_duration
).sum()

print("========== ADVANCED VALIDATION ==========")

print("Missing 15-minute intervals:", missing_intervals)
print("Invalid High values:", invalid_high)
print("Invalid Low values:", invalid_low)
print("Invalid prices:", invalid_prices)
print("Invalid volume:", invalid_volume)
print("Invalid candle duration:", invalid_duration)

print("\nFirst date:", df["Open_Time"].min())
print("Last date:", df["Open_Time"].max())

if all(x == 0 for x in [
    missing_intervals,
    invalid_high,
    invalid_low,
    invalid_prices,
    invalid_volume,
    invalid_duration
]):
    print("\nDATASET PASSED ADVANCED VALIDATION")
else:
    print("\nDATASET NEEDS FURTHER INVESTIGATION")
