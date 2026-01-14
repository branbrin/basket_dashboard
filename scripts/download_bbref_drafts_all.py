import time
import random
from pathlib import Path

import pandas as pd
import requests

def project_paths():
    project_root = Path(__file__).resolve().parent.parent
    raw_dir = project_root / "data_raw" / "bbref"
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_path = raw_dir / "bbref_draft_all.csv"
    return out_path

def fetch_draft_year(year: int) -> pd.DataFrame:
    url = f"https://www.basketball-reference.com/draft/NBA_{year}.html"
    headers = {
        "User-Agent": "Mozilla/5.0",
    }
    r = requests.get(url, headers=headers, timeout=60)
    r.raise_for_status()

    # Basketball-Reference tables can be parsed via read_html
    tables = pd.read_html(r.text)
    # The main draft table is usually the first one
    df = tables[0].copy()
    df["draft_year"] = year
    return df

def main():
    out_path = project_paths()

    # NBA draft years on BBRef start 1947
    years = list(range(1947, 2025))

    all_dfs = []
    for i, y in enumerate(years, start=1):
        print(f"[{i}/{len(years)}] Draft {y}")
        try:
            df = fetch_draft_year(y)
            all_dfs.append(df)
        except Exception as e:
            print(f"  ERROR year={y}: {e}")
            continue

        # polite delay
        time.sleep(1.5 + random.uniform(0, 1.0))

    master = pd.concat(all_dfs, ignore_index=True)
    master.to_csv(out_path, index=False)
    print(f"\nSaved: {out_path} | rows={len(master)} | cols={len(master.columns)}")

if __name__ == "__main__":
    main()
