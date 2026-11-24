from pathlib import Path
import pandas as pd

RAW = Path("data/raw")

for csv_path in sorted(RAW.glob("*.csv")):
    df = pd.read_csv(csv_path)
    print(f"{csv_path.name}: {len(df):,} rows, {df.shape[1]} columns")
    print("   columns:", ", ".join(df.columns))
    print()