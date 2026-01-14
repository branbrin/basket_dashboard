import time
from pathlib import Path

import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats


def get_nba_season_stats(
    season: str,
    season_type: str = "Regular Season",
    per_mode: str = "PerGame"
) -> pd.DataFrame:
    """
    Download NBA player stats for a given season using the NBA Stats API.

    Parameters
    ----------
    season : str
        NBA season in format "YYYY-YY", e.g. "2023-24".
    season_type : str
        "Regular Season", "Playoffs", etc.
    per_mode : str
        "PerGame", "Totals", "Per36", ...

    Returns
    -------
    pd.DataFrame
        DataFrame with player stats.
    """
    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        season_type_all_star=season_type,
        per_mode_detailed=per_mode,
    )
    df = stats.get_data_frames()[0]

    # Add metadata columns so later concatenation is easier
    df["Season"] = season
    df["SeasonType"] = season_type
    df["PerMode"] = per_mode

    return df


def main():
    # --------------------------
    # 1) Seasons to download
    # --------------------------
    seasons = [
        "2018-19",
        "2019-20",
        "2020-21",
        "2021-22",
        "2022-23",
        "2023-24",
    ]

    # You can include "Playoffs" later if you want
    season_types = [
        "Regular Season",
        # "Playoffs",
    ]

    per_modes = [
        "PerGame",
        "Totals",
    ]

    # --------------------------
    # 2) Output directory
    # --------------------------
    project_root = Path(__file__).resolve().parent.parent
    out_dir = project_root / "data_raw" / "nba"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Output directory: {out_dir}")

    # --------------------------
    # 3) Loop over seasons / types / per_modes
    # --------------------------
    for season in seasons:
        for season_type in season_types:
            for per_mode in per_modes:
                print(
                    f"\n=== Downloading NBA stats for {season} "
                    f"({season_type}, {per_mode}) ==="
                )

                try:
                    df = get_nba_season_stats(
                        season=season,
                        season_type=season_type,
                        per_mode=per_mode,
                    )
                except Exception as e:
                    print(f"Error downloading {season} {season_type} {per_mode}: {e}")
                    time.sleep(3)
                    continue

                # Build output path, e.g.:
                # nba_players_201819_regularseason_pergame.csv
                season_flat = season.replace("-", "")
                season_type_token = season_type.lower().replace(" ", "")
                per_mode_token = per_mode.lower()

                filename = (
                    f"nba_players_{season_flat}_"
                    f"{season_type_token}_{per_mode_token}.csv"
                )
                out_path = out_dir / filename

                df.to_csv(out_path, index=False)
                print(f"Saved {len(df)} rows to {out_path}")

                # Be nice to the API
                time.sleep(1.5)


if __name__ == "__main__":
    main()