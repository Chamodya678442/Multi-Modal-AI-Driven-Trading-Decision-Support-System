import pandas as pd

df = pd.read_csv("data/BTCUSDT_15m_1year.csv")

timestamp = int(df["Open_Time"].iloc[0])

unit = "us" if timestamp > 10**14 else "ms"

df["Open_Time"] = pd.to_datetime(
    df["Open_Time"],
    unit=unit,
    utc=True
)

print("Detected timestamp unit:", unit)
print(df["Open_Time"].head())

