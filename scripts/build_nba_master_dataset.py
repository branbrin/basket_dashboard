from pathlib import Path
import pandas as pd


def main():
    # Locate project root and folders
    project_root = Path(__file__).resolve().parent.parent
    raw_dir = project_root / "data_raw" / "nba"
    processed_dir = project_root / "data_processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    print(f"Reading raw files from: {raw_dir}")

    # Collect all CSV files that follow our naming pattern
    csv_files = sorted(raw_dir.glob("nba_players_*.csv"))

    if not csv_files:
        print("No NBA CSV files found in data_raw/nba. Run download_nba_seasons.py first.")
        return

    all_dfs = []

    for path in csv_files:
        print(f"Loading {path.name} ...")
        df = pd.read_csv(path)

        # Safety check: ensure metadata columns exist
        if "Season" not in df.columns or "SeasonType" not in df.columns or "PerMode" not in df.columns:
            print(f"Warning: file {path.name} has no metadata columns. Skipping.")
            continue

        all_dfs.append(df)

    if not all_dfs:
        print("No valid files with metadata found. Nothing to save.")
        return

    # Concatenate everything
    master_df = pd.concat(all_dfs, axis=0, ignore_index=True)

    out_path = processed_dir / "nba_players_all.csv"
    master_df.to_csv(out_path, index=False)

    print(f"\nMaster dataset saved: {out_path}")
    print(f"Total rows: {len(master_df)}")
    print(f"Columns: {list(master_df.columns)}")


if __name__ == "__main__":
    main()
