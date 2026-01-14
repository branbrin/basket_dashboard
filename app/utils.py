from pathlib import Path
import pandas as pd
import streamlit as st

MASTER_ALL = Path("data_processed/master_all_leagues.csv")

@st.cache_data(show_spinner=False)
def load_master() -> pd.DataFrame:
    df = pd.read_csv(MASTER_ALL)

    # Seguridad: columnas clave
    if "league" not in df.columns:
        df["league"] = df.get("lg", "UNKNOWN")
    if "lg" not in df.columns:
        df["lg"] = df["league"]

    # Tipos (para sliders/ordenaciones)
    num_cols = [
        "season_start_year", "age", "g", "mp_per_game",
        "pts_per_game", "ast_per_game", "trb_per_game",
        "orb_per_game", "drb_per_game",
        "stl_per_game", "blk_per_game", "tov_per_game", "pf_per_game",
        "fg_percent", "x3p_percent", "ft_percent",
        "draft_year", "draft_round", "draft_pick",
        "career_year", "rookie_season_start_year",
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df
