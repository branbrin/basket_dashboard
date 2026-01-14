from pathlib import Path
import pandas as pd

def normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df

def main():
    project_root = Path(__file__).resolve().parent.parent
    processed_dir = project_root / "data_processed"

    stats_path = processed_dir / "nba_player_per_game_normalized.csv"
    draft_path = processed_dir / "nba_draft_history_normalized.csv"

    stats = normalize_cols(pd.read_csv(stats_path))
    draft = normalize_cols(pd.read_csv(draft_path))

    print("STATS columns:", stats.columns.tolist())
    print("DRAFT columns:", draft.columns.tolist())

    # --- Standardize draft column names ---
    # Your draft columns are: ['draft_year','lg','draft_pick','draft_round','tm','player','player_id','college']
    draft = draft.rename(columns={
        "tm": "draft_team",
        "player": "player_name",
    })

    # Ensure required columns exist
    required_stats = ["player_id", "player_name", "season", "lg"]
    required_draft = ["player_id", "draft_year", "draft_round", "draft_pick", "draft_team", "college"]

    missing_stats = [c for c in required_stats if c not in stats.columns]
    missing_draft = [c for c in required_draft if c not in draft.columns]

    if missing_stats:
        raise ValueError(f"Stats missing columns: {missing_stats}")
    if missing_draft:
        raise ValueError(f"Draft missing columns: {missing_draft}")

    # --- Merge by player_id (best key) ---
    master = stats.merge(
        draft[required_draft],
        on="player_id",
        how="left",
        suffixes=("", "_draft")
    )

    # Optional: if player_name differs between stats and draft, keep stats as source of truth
    # but you can inspect mismatches later.
    # master["player_name"] is from stats, master["player_name_draft"] would exist only if we merged it.

    out_csv = processed_dir / "nba_master.csv"
    master.to_csv(out_csv, index=False)

    print(f"\nSaved master CSV: {out_csv}")
    print(f"Rows: {len(master)} | Cols: {len(master.columns)}")

    # Quick coverage checks
    draft_coverage = master["draft_year"].notna().mean() * 100
    print(f"Draft coverage: {draft_coverage:.1f}%")

    # How many distinct players in stats vs draft
    print(f"Distinct players (stats): {stats['player_id'].nunique()}")
    print(f"Distinct players (draft): {draft['player_id'].nunique()}")

if __name__ == "__main__":
    main()
