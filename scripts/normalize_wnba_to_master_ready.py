import pandas as pd
from pathlib import Path

IN_PATH = Path("data_raw/wnba/wnba_normalized.csv")
OUT_PATH = Path("data_processed/wnba_master_ready.csv")


def _coerce_numeric(df: pd.DataFrame, cols: list[str]) -> None:
    """In-place numeric coercion."""
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")


def main():
    if not IN_PATH.exists():
        raise FileNotFoundError(f"No existe el input: {IN_PATH.resolve()}")

    df = pd.read_csv(IN_PATH)

    # --- 1) Resolver columnas duplicadas típicas de tu CSV (G/G.1, MP/MP.1) ---
    # Preferimos la versión "por partido" si existe (MP.1 suele ser MP/G en exports raros),
    # pero en tu CSV ya dices que son per-game; así que hacemos:
    # - G: nos quedamos con G si tiene datos; si no, usamos G.1
    # - MP: preferimos MP.1 si parece per-game (valores típicos 5-40), si no MP
    if "G.1" in df.columns and "G" in df.columns:
        # Si G es NaN y G.1 no, rellena
        df["G"] = df["G"].fillna(df["G.1"])
        df = df.drop(columns=["G.1"])

    if "MP.1" in df.columns and "MP" in df.columns:
        # Heurística simple: si MP.1 parece per-game (máximo <= 60) la usamos como mpg
        mp1 = pd.to_numeric(df["MP.1"], errors="coerce")
        mp0 = pd.to_numeric(df["MP"], errors="coerce")
        use_mp1 = mp1.notna().sum() >= mp0.notna().sum() and (mp1.max(skipna=True) <= 60)
        if use_mp1:
            df["MP"] = df["MP.1"]
        df = df.drop(columns=["MP.1"])

    # --- 2) Renombrado a estándar master (NBA-like) ---
    rename_map = {
        "player": "player_name",
        "Player": "player_name",
        "Team": "team",
        "Pos": "pos",
        "G": "g",

        # per-game / percent
        "MP": "mp_per_game",
        "FG": "fg_per_game",
        "FGA": "fga_per_game",
        "FG%": "fg_percent",
        "3P": "x3p_per_game",
        "3PA": "x3pa_per_game",
        "3P%": "x3p_percent",
        "2P": "x2p_per_game",
        "2PA": "x2pa_per_game",
        "2P%": "x2p_percent",
        "FT": "ft_per_game",
        "FTA": "fta_per_game",
        "FT%": "ft_percent",

        # rebotes y demás
        "ORB": "orb_per_game",
        # ojo: tu WNBA trae TRB pero no DRB; TRB=rebotes totales
        "TRB": "trb_per_game",
        "AST": "ast_per_game",
        "STL": "stl_per_game",
        "BLK": "blk_per_game",
        "TOV": "tov_per_game",
        "PF": "pf_per_game",
        "PTS": "pts_per_game",
    }

    # Aplica renombrado solo si la columna existe
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # --- 3) Crear / asegurar columnas clave ---
    # league / lg
    df["league"] = "WNBA"
    df["lg"] = "WNBA"

    # season: en tu WNBA lo tienes como 'season' con 1997, 1998... (año)
    # Convertimos a formato "YYYY-YY" para que sea comparable con NBA y te vaya bien en Streamlit.
    # Ej: 1997 -> "1997-98"
    if "season" in df.columns:
        df["season_start_year"] = pd.to_numeric(df["season"], errors="coerce")
    elif "season_start_year" in df.columns:
        df["season_start_year"] = pd.to_numeric(df["season_start_year"], errors="coerce")
    else:
        raise KeyError("No encuentro columna 'season' ni 'season_start_year' en el WNBA normalizado.")

    df["season"] = df["season_start_year"].apply(
        lambda y: f"{int(y)}-{str(int(y)+1)[-2:]}" if pd.notna(y) else pd.NA
    )

    # player_id: WNBA no suele traer; lo dejamos vacío para no romper joins
    if "player_id" not in df.columns:
        df["player_id"] = pd.NA

    # draft fields (WNBA no; los dejamos como NA para esquema común)
    for c in ["draft_year", "draft_round", "draft_pick", "draft_team", "college"]:
        if c not in df.columns:
            df[c] = pd.NA

    # rookie/career (si ya lo tienes, genial; si no, lo calculamos)
    if "rookie_season_start_year" not in df.columns or "career_year" not in df.columns:
        rookie = (
            df.dropna(subset=["season_start_year"])
              .groupby("player_name", as_index=False)["season_start_year"]
              .min()
              .rename(columns={"season_start_year": "rookie_season_start_year"})
        )
        df = df.merge(rookie, on="player_name", how="left")
        df["career_year"] = df["season_start_year"] - df["rookie_season_start_year"] + 1

    # --- 4) Coerción numérica de métricas clave ---
    numeric_cols = [
        "season_start_year", "age", "g", "mp_per_game",
        "fg_per_game", "fga_per_game", "fg_percent",
        "x3p_per_game", "x3pa_per_game", "x3p_percent",
        "x2p_per_game", "x2pa_per_game", "x2p_percent",
        "ft_per_game", "fta_per_game", "ft_percent",
        "orb_per_game", "trb_per_game", "ast_per_game",
        "stl_per_game", "blk_per_game", "tov_per_game",
        "pf_per_game", "pts_per_game",
        "rookie_season_start_year", "career_year",
    ]
    _coerce_numeric(df, numeric_cols)

    # --- 5) Orden de columnas recomendado (sin eliminar otras) ---
    preferred = [
        "league", "lg",
        "season", "season_start_year",
        "player_name", "player_id",
        "team", "pos", "age", "g",
        "mp_per_game",
        "pts_per_game", "ast_per_game", "trb_per_game", "orb_per_game",
        "fg_per_game", "fga_per_game", "fg_percent",
        "x3p_per_game", "x3pa_per_game", "x3p_percent",
        "x2p_per_game", "x2pa_per_game", "x2p_percent",
        "ft_per_game", "fta_per_game", "ft_percent",
        "stl_per_game", "blk_per_game", "tov_per_game", "pf_per_game",
        "draft_year", "draft_round", "draft_pick", "draft_team", "college",
        "rookie_season_start_year", "career_year",
    ]
    cols = [c for c in preferred if c in df.columns] + [c for c in df.columns if c not in preferred]
    df = df[cols]

    # --- 6) Guardar ---
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)

    # --- 7) Checks útiles ---
    print(f"Saved: {OUT_PATH.resolve()}")
    print(f"Rows: {len(df)} | Cols: {len(df.columns)}")
    print("League counts:")
    print(df["league"].value_counts(dropna=False))
    print("Missing league:", df["league"].isna().sum(), "| Missing lg:", df["lg"].isna().sum())
    print("Season_start_year min/max:", df["season_start_year"].min(), df["season_start_year"].max())


if __name__ == "__main__":
    main()

