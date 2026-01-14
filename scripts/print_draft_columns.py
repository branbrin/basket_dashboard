import pandas as pd
from pathlib import Path

p = Path("data_processed/nba_draft_history_normalized.csv")
df = pd.read_csv(p)

print(df.columns.tolist())
