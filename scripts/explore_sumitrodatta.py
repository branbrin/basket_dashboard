from pathlib import Path
import pandas as pd

def main():
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data_raw" / "kaggle" / "sumitrodatta"

    per_game = pd.read_csv(data_dir / "Player Per Game.csv")
    draft = pd.read_csv(data_dir / "Draft Pick History.csv")

    print("=== Player Per Game ===")
    print(per_game.shape)
    print(per_game.columns.tolist())
    print(per_game.head(3))

    print("\n=== Draft Pick History ===")
    print(draft.shape)
    print(draft.columns.tolist())
    print(draft.head(3))

if __name__ == "__main__":
    main()
