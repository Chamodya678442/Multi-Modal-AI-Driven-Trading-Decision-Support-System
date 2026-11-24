
import pandas as pd
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
file_path = project_root / "data" / "BTCUSDT_15m_1year.csv"

df = pd.read_csv(file_path)

print("========== DATASET SUMMARY ==========")

print("Total records:", len(df))
print("Total columns:", len(df.columns))

print("\nColumn names:")
print(df.columns.tolist())

print("\nFirst 5 records:")
print(df.head())

print("\nLast 5 records:")
print(df.tail())

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate timestamps:")
print(df["Open_Time"].duplicated().sum())

print("\nData types:")
print(df.dtypes)

print("\n========== VALIDATION ==========")

print("Missing records:", df.isnull().sum().sum())

print("Duplicate records:",
      df.duplicated(subset=["Open_Time"]).sum())

print("Dataset size:",
      Path(file_path).stat().st_size / (1024 * 1024),
      "MB")
