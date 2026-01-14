from pathlib import Path
import pandas as pd

def main():
    project_root = Path(__file__).resolve().parent.parent
    raw_dir = project_root / "data_raw" / "kaggle" / "sumitrodatta"
    processed_dir = project_root / "data_processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Load
    per_game = pd.read_csv(raw_dir / "Player Per Game.csv")
    draft = pd.read_csv(raw_dir / "Draft Pick History.csv")

    # --- Normalize column names ---
    per_game.columns = (
        per_game.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    draft.columns = (
        draft.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Rename key columns for clarity
    per_game = per_game.rename(columns={
        "player": "player_name",
        "season": "season"
    })

    draft = draft.rename(columns={
    "season": "draft_year",
    "round": "draft_round",
    "overall_pick": "draft_pick",
    })

    # Save normalized versions
    per_game.to_csv(processed_dir / "nba_player_per_game_normalized.csv", index=False)
    draft.to_csv(processed_dir / "nba_draft_history_normalized.csv", index=False)

    print("Normalized files saved in data_processed/")

if __name__ == "__main__":
    main()
