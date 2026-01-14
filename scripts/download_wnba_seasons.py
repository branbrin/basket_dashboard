import time
import random
from pathlib import Path

import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.library.parameters import SeasonTypeAllStar, PerModeDetailed


# ---- Config ----
OUT_DIR = Path("data_raw/wnba")
OUT_DIR.mkdir(parents=True, exist_ok=True)

SEASON_TYPE = "Regular Season"
PER_MODE = PerModeDetailed.perGame             # "PerGame"

# WNBA on stats.nba.com uses league_id="10"
LEAGUE_ID_WNBA = "10"

# You can tune these if you keep getting throttled/timeouts
SLEEP_BETWEEN_CALLS_SEC = (1.2, 2.3)  # random sleep range between requests
MAX_RETRIES = 6
TIMEOUT_SEC = 60  # nba_api uses requests under the hood; timeout is handled internally in most cases


def season_label_for_year(year: int) -> str:
    """
    WNBA seasons are typically referred by a single year like "2023".
    """
    return str(year)


def fetch_wnba_player_stats(season_year: int) -> pd.DataFrame:
    """
    Download WNBA per-player stats for a given season year.
    """
    season = season_label_for_year(season_year)

    # nba_api endpoints accept **parameters**; league_id="10" is key for WNBA.
    endpoint = leaguedashplayerstats.LeagueDashPlayerStats(
        league_id=LEAGUE_ID_WNBA,
        season=season,
        season_type_all_star=SEASON_TYPE,
        per_mode_detailed=PER_MODE,
        timeout=TIMEOUT_SEC,
    )
    df = endpoint.get_data_frames()[0]

    # Add minimal metadata
    df["Season"] = season
    df["SeasonType"] = "Regular Season"
    df["PerMode"] = "PerGame"
    df["lg"] = "WNBA"
    df["season_start_year"] = season_year

    return df


def fetch_with_retries(season_year: int) -> pd.DataFrame | None:
    """
    Retry with exponential backoff + jitter.
    Returns None if it ultimately fails.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            df = fetch_wnba_player_stats(season_year)
            return df
        except Exception as e:
            wait = min(60, (2 ** (attempt - 1))) + random.uniform(0.0, 1.0)
            print(f"[{season_year}] ERROR attempt {attempt}/{MAX_RETRIES}: {e}")
            if attempt < MAX_RETRIES:
                print(f"[{season_year}] retrying in {wait:.1f}s ...")
                time.sleep(wait)
            else:
                print(f"[{season_year}] giving up.")
                return None


def main():
    # WNBA started 1997
    start_year = 1997
    end_year = pd.Timestamp.today().year  # current year

    all_dfs = []
    ok, fail, skipped = 0, 0, 0

    print(f"Downloading WNBA seasons {start_year}..{end_year} (Regular Season, PerGame)")

    for i, year in enumerate(range(start_year, end_year + 1), start=1):
        out_csv = OUT_DIR / f"wnba_players_{year}.csv"

        # Skip if already downloaded
        if out_csv.exists() and out_csv.stat().st_size > 0:
            print(f"[{i}/{end_year - start_year + 1}] {year} -> already exists, skip")
            skipped += 1
            continue

        print(f"[{i}/{end_year - start_year + 1}] {year} -> downloading...")

        df = fetch_with_retries(year)
        if df is None or df.empty:
            fail += 1
            continue

        df.to_csv(out_csv, index=False)
        print(f"[{year}] saved -> {out_csv} (rows={len(df)})")

        all_dfs.append(df)
        ok += 1

        # polite sleep (avoid throttling)
        time.sleep(random.uniform(*SLEEP_BETWEEN_CALLS_SEC))

    # Build a combined file from whatever we managed to download this run
    if all_dfs:
        master = pd.concat(all_dfs, ignore_index=True)
        master_csv = OUT_DIR / "wnba_players_all_seasons_raw.csv"
        master.to_csv(master_csv, index=False)
        print(f"\n✅ Combined file saved: {master_csv} (rows={len(master)})")
    else:
        print("\n⚠️ No seasons downloaded in this run (maybe all were skipped or all failed).")

    print(f"\nSummary: ok={ok} skipped={skipped} failed={fail}")


if __name__ == "__main__":
    main()
