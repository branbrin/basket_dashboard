from pathlib import Path
import pandas as pd

def parse_season_start(season_val: str):
    # Handles "2018-19", "2003-04" and also numeric seasons if any
    if pd.isna(season_val):
        return None
    s = str(season_val).strip()
    # If format like "2018-19"
    if "-" in s:
        try:
            return int(s.split("-")[0])
        except Exception:
            return None
    # If already a year like 2018
    try:
        return int(float(s))
    except Exception:
        return None

def main():
    project_root = Path(__file__).resolve().parent.parent
    processed_dir = project_root / "data_processed"

    in_path = processed_dir / "nba_master.csv"
    out_path = processed_dir / "nba_master_ready.csv"

    df = pd.read_csv(in_path)

    # Season start year
    df["season_start_year"] = df["season"].apply(parse_season_start)

    # Draft flags
    df["drafted_flag"] = df["draft_year"].notna()
    df["undrafted_flag"] = ~df["drafted_flag"]

    # Ensure numeric types for picks/rounds
    for col in ["draft_year", "draft_round", "draft_pick"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Optional: keep only NBA league rows if you want NBA-only dashboard (later you decide)
    # df = df[df["lg"] == "NBA"].copy()

    df.to_csv(out_path, index=False)

    print(f"Saved dashboard-ready CSV: {out_path}")
    print(f"Rows: {len(df)} | Cols: {len(df.columns)}")
    print(f"Undrafted rows: {df['undrafted_flag'].mean()*100:.1f}%")

if __name__ == "__main__":
    main()
