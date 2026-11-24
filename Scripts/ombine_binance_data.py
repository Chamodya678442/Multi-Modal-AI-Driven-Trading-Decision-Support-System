
import pandas as pd
from pathlib import Path
import glob

project_root = Path(__file__).resolve().parent.parent

# Input folder
folder = project_root / "data" / "extracted"

# Binance Kline columns
columns = [
    "Open_Time",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "Close_Time",
    "Quote_Volume",
    "Number_of_Trades",
    "Taker_Buy_Base",
    "Taker_Buy_Quote",
    "Ignore"
]

files = glob.glob(str(folder / "*.csv"))

dataframes = []

for file in files:
    print("Reading:", file)

    df = pd.read_csv(
        file,
        header=None,
        names=columns
    )

    dataframes.append(df)

# Combine all monthly files
combined = pd.concat(
    dataframes,
    ignore_index=True
)

# Remove duplicate candles
combined = combined.drop_duplicates(
    subset=["Open_Time"]
)

# Sort by timestamp
combined = combined.sort_values("Open_Time")

# Save final dataset
output = project_root / "data" / "BTCUSDT_15m_1year.csv"

combined.to_csv(output, index=False)

print("\nDataset created successfully!")
print("Total records:", len(combined))
print("Output:", output)
