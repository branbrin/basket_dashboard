from pathlib import Path
import pandas as pd
from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo
import time

def download_draft_info():
    # Get list of all NBA players known by nba_api
    player_list = players.get_players()
    records = []

    for p in player_list:
        pid = p["id"]

        try:
            info = commonplayerinfo.CommonPlayerInfo(player_id=pid).get_data_frames()[0]
            record = {
                "player_id": pid,
                "full_name": p["full_name"],
                "first_name": p["first_name"],
                "last_name": p["last_name"],
                "draft_year": info.get("DRAFT_YEAR", None),
                "draft_round": info.get("DRAFT_ROUND", None),
                "draft_number": info.get("DRAFT_NUMBER", None),
                "from_year": info.get("FROM_YEAR", None),
                "to_year": info.get("TO_YEAR", None),
                "team_id": info.get("TEAM_ID", None),
            }
            records.append(record)

        except Exception as e:
            print(f"Error with player_id={pid}: {e}")
            time.sleep(2)
            continue

        time.sleep(0.6)

    df = pd.DataFrame(records)
    return df


if __name__ == "__main__":
    df_draft = download_draft_info()

    out_path = "../data_raw/nba/nba_draft_info.csv"
    df_draft.to_csv(out_path, index=False)
    print("Saved draft info to", out_path)