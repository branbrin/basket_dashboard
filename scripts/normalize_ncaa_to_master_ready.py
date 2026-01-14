import pandas as pd
from pathlib import Path

IN_PATH = Path("data_raw/ncaa/ncaa-stats-complete.csv")
OUT_PATH = Path("data_processed/ncaa_master_ready.csv")


def _coerce_numeric(df: pd.DataFrame, cols: list[str]) -> None:
    """In-place numeric coercion."""
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")


def main():
    if not IN_PATH.exists():
        raise FileNotFoundError(f"No existe el input: {IN_PATH.resolve()}")

    df = pd.read_csv(IN_PATH)

    # --- 1) Renombrar columnas NCAA -> esquema master ---
    # Tu CSV:
    # player,cls,year,gp,mpg,ppg,fgm,fga,fg%,3pm,3pa,3p%,ftm,fta,ft%,orb,drb,rpg,apg,spg,bpg,tov,pf
    rename_map = {
        "player": "player_name",
        "year": "season_start_year",   # aquí "year" es la temporada (ej. 2003)
        "gp": "g",
        "mpg": "mp_per_game",
        "ppg": "pts_per_game",
        "apg": "ast_per_game",
        "rpg": "trb_per_game",         # rebotes totales por partido
        "orb": "orb_per_game",
        "drb": "drb_per_game",
        "spg": "stl_per_game",
        "bpg": "blk_per_game",
        "tov": "tov_per_game",
        "pf": "pf_per_game",
        "fgm": "fg_per_game",
        "fga": "fga_per_game",
        "fg%": "fg_percent",
        "3pm": "x3p_per_game",
        "3pa": "x3pa_per_game",
        "3p%": "x3p_percent",
        "ftm": "ft_per_game",
        "fta": "fta_per_game",
        "ft%": "ft_percent",
        "cls": "class",
    }

    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # --- 2) Añadir league/lg ---
    df["league"] = "NCAA"
    df["lg"] = "NCAA"

    # --- 3) Crear columnas obligatorias del master si faltan ---
    # NCAA no trae team/pos/age/player_id/draft_*
    for c in ["team", "pos", "age", "player_id"]:
        if c not in df.columns:
            df[c] = pd.NA

    for c in ["draft_year", "draft_round", "draft_pick", "draft_team", "college"]:
        if c not in df.columns:
            df[c] = pd.NA

    # Season en formato comparable.
    # Para NCAA usamos "YYYY" (o "YYYY-YY" si quisieras),
    # pero tu Explorer usa season para selectbox; lo más simple: "YYYY"
    df["season_start_year"] = pd.to_numeric(df["season_start_year"], errors="coerce")
    df["season"] = df["season_start_year"].apply(lambda y: f"{int(y)}" if pd.notna(y) else pd.NA)

    # --- 4) Calcular rookie/career normalizado dentro de NCAA ---
    # (Ojo: "rookie" aquí sería 1er año NCAA que aparece, no rookie NBA)
    rookie = (
        df.dropna(subset=["season_start_year"])
          .groupby("player_name", as_index=False)["season_start_year"]
          .min()
          .rename(columns={"season_start_year": "rookie_season_start_year"})
    )
    df = df.merge(rookie, on="player_name", how="left")
    df["career_year"] = df["season_start_year"] - df["rookie_season_start_year"] + 1

    # --- 5) Numeric coercion ---
    numeric_cols = [
        "season_start_year", "age", "g", "mp_per_game",
        "pts_per_game", "ast_per_game", "trb_per_game",
        "orb_per_game", "drb_per_game",
        "fg_per_game", "fga_per_game", "fg_percent",
        "x3p_per_game", "x3pa_per_game", "x3p_percent",
        "ft_per_game", "fta_per_game", "ft_percent",
        "stl_per_game", "blk_per_game", "tov_per_game", "pf_per_game",
        "rookie_season_start_year", "career_year",
    ]
    _coerce_numeric(df, numeric_cols)

    # --- 6) Orden recomendado ---
    preferred = [
        "league", "lg",
        "season", "season_start_year",
        "player_name", "player_id",
        "team", "pos", "age", "g",
        "mp_per_game",
        "pts_per_game", "ast_per_game", "trb_per_game", "orb_per_game", "drb_per_game",
        "fg_per_game", "fga_per_game", "fg_percent",
        "x3p_per_game", "x3pa_per_game", "x3p_percent",
        "ft_per_game", "fta_per_game", "ft_percent",
        "stl_per_game", "blk_per_game", "tov_per_game", "pf_per_game",
        "draft_year", "draft_round", "draft_pick", "draft_team", "college",
        "rookie_season_start_year", "career_year",
        "class",
    ]
    cols = [c for c in preferred if c in df.columns] + [c for c in df.columns if c not in preferred]
    df = df[cols]

    # --- 7) Guardar ---
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)

    # --- 8) Checks ---
    print(f"Saved: {OUT_PATH.resolve()}")
    print(f"Rows: {len(df)} | Cols: {len(df.columns)}")
    print("League counts:")
    print(df["league"].value_counts(dropna=False))
    print("Missing league:", df["league"].isna().sum(), "| Missing lg:", df["lg"].isna().sum())
    print("Season_start_year min/max:", df["season_start_year"].min(), df["season_start_year"].max())


if __name__ == "__main__":
    main()
