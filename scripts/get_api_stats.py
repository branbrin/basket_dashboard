from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd
from pathlib import Path

def get_nba_season_stats(season: str):
    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        season_type_all_star="Regular Season",
        per_mode_detailed="PerGame",
    )
    return stats.get_data_frames()[0]

if __name__ == "__main__":
    season = "2023-24"
    df_nba = get_nba_season_stats(season)

    # Ruta correcta esté donde estés:
    project_root = Path(__file__).resolve().parent.parent
    out_dir = project_root / "data_raw" / "nba"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f"nba_players_{season.replace('-', '')}.csv"

    df_nba.to_csv(out_path, index=False)
    print(f"Saved NBA stats for {season} in {out_path}")