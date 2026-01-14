import pandas as pd
from pathlib import Path

NBA_PATH  = Path("data_processed/nba_master_ready.csv")   # AJUSTA si tu NBA está en otra ruta/nombre
WNBA_PATH = Path("data_processed/wnba_master_ready.csv")
NCAA_PATH = Path("data_processed/ncaa_master_ready.csv")

OUT_PATH  = Path("data_processed/master_all_leagues.csv")


# Columnas "core" que queremos tener siempre (aunque sea con NA)
CORE_COLS = [
    "league", "lg",
    "season", "season_start_year",
    "player_name", "player_id",
    "team", "pos", "age", "g",
    "mp_per_game",
    "pts_per_game", "ast_per_game", "trb_per_game",
    "orb_per_game", "drb_per_game",
    "stl_per_game", "blk_per_game", "tov_per_game", "pf_per_game",
    "fg_per_game", "fga_per_game", "fg_percent",
    "x3p_per_game", "x3pa_per_game", "x3p_percent",
    "ft_per_game", "fta_per_game", "ft_percent",
    "draft_year", "draft_round", "draft_pick", "draft_team", "college",
    "rookie_season_start_year", "career_year",
]


def ensure_league_cols(df: pd.DataFrame, league_value: str) -> pd.DataFrame:
    df = df.copy()

    # Si no existe, la creamos
    if "league" not in df.columns:
        df["league"] = league_value
    if "lg" not in df.columns:
        df["lg"] = league_value

    # Si está vacía o NaN, la rellenamos
    df["league"] = df["league"].fillna(league_value)
    df.loc[df["league"].astype(str).str.strip().eq(""), "league"] = league_value

    df["lg"] = df["lg"].fillna(league_value)
    df.loc[df["lg"].astype(str).str.strip().eq(""), "lg"] = league_value

    return df


def ensure_columns(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    df = df.copy()
    for c in cols:
        if c not in df.columns:
            df[c] = pd.NA
    return df


def coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    numeric_cols = [
        "season_start_year", "age", "g", "mp_per_game",
        "pts_per_game", "ast_per_game", "trb_per_game",
        "orb_per_game", "drb_per_game",
        "stl_per_game", "blk_per_game", "tov_per_game", "pf_per_game",
        "fg_per_game", "fga_per_game", "fg_percent",
        "x3p_per_game", "x3pa_per_game", "x3p_percent",
        "ft_per_game", "fta_per_game", "ft_percent",
        "draft_year", "draft_round", "draft_pick",
        "rookie_season_start_year", "career_year",
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def reorder_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in CORE_COLS if c in df.columns] + [c for c in df.columns if c not in CORE_COLS]
    return df[cols]


def load_csv(path: Path, league_value: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe: {path.resolve()}")
    df = pd.read_csv(path)

    df = ensure_league_cols(df, league_value)
    df = ensure_columns(df, CORE_COLS)

    # Derivar season_start_year si faltara (por seguridad)
    if df["season_start_year"].isna().all() and "season" in df.columns:
        # "2018-19" -> 2018  (si aplica)
        tmp = df["season"].astype(str).str.slice(0, 4)
        df["season_start_year"] = pd.to_numeric(tmp, errors="coerce")

    # Derivar season si faltara
    if df["season"].isna().all() and "season_start_year" in df.columns:
        df["season"] = df["season_start_year"].apply(lambda y: f"{int(y)}" if pd.notna(y) else pd.NA)

    df = coerce_numeric(df)
    df = reorder_columns(df)
    return df


def main():
    nba  = load_csv(NBA_PATH,  "NBA")
    wnba = load_csv(WNBA_PATH, "WNBA")
    ncaa = load_csv(NCAA_PATH, "NCAA")

    master = pd.concat([nba, wnba, ncaa], ignore_index=True)

    # --- Validaciones clave ---
    # 1) Nunca vacíos
    master["league"] = master["league"].fillna("UNKNOWN")
    master.loc[master["league"].astype(str).str.strip().eq(""), "league"] = "UNKNOWN"
    master["lg"] = master["lg"].fillna(master["league"])
    master.loc[master["lg"].astype(str).str.strip().eq(""), "lg"] = master["league"]

    # 2) Tipos útiles
    master = coerce_numeric(master)

    # 3) Orden final
    master = reorder_columns(master)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    master.to_csv(OUT_PATH, index=False)

    print(f"Saved: {OUT_PATH.resolve()}")
    print(f"Rows: {len(master)} | Cols: {len(master.columns)}")
    print("League counts:")
    print(master["league"].value_counts(dropna=False))
    print("Missing league:", master["league"].isna().sum(), "| Missing lg:", master["lg"].isna().sum())


if __name__ == "__main__":
    main()
