import pandas as pd
from pathlib import Path


def main():
    in_path = Path("data_raw/ncaa/ncaa-stats-complete.csv")
    out_path = Path("data_processed/ncaa_players_normalized.csv")

    df = pd.read_csv(in_path)

    # Renombrar columnas
    df = df.rename(columns={
        "player": "player_name",
        "gp": "g",
        "mpg": "mp_per_game",
        "ppg": "pts_per_game",
        "apg": "ast_per_game",
        "rpg": "trb_per_game",
        "orb": "orb_per_game",
        "drb": "drb_per_game",
        "spg": "stl_per_game",
        "bpg": "blk_per_game",
        "tov": "tov_per_game",
        "fg%": "fg_percent",
        "3p%": "x3p_percent",
        "ft%": "ft_percent",
        "cls": "class_year",
        "year": "season_start_year",
    })

    # Liga
    df["lg"] = "NCAA"

    # Season tipo "2003-04"
    df["season"] = df["season_start_year"].astype(int).astype(str) + "-" + (
        (df["season_start_year"] + 1).astype(int).astype(str).str[-2:]
    )

    # Columnas que no existen en NCAA pero sí en el master
    df["team"] = pd.NA
    df["pos"] = pd.NA
    df["player_id"] = pd.NA

    # Seleccionar columnas finales (alineadas con tu Explorador)
    final_cols = [
        "player_name",
        "player_id",
        "lg",
        "season",
        "season_start_year",
        "team",
        "pos",
        "class_year",
        "g",
        "mp_per_game",
        "pts_per_game",
        "ast_per_game",
        "trb_per_game",
        "orb_per_game",
        "drb_per_game",
        "stl_per_game",
        "blk_per_game",
        "tov_per_game",
        "fg_percent",
        "x3p_percent",
        "ft_percent",
    ]

    final_cols = [c for c in final_cols if c in df.columns]
    df = df[final_cols]

    # Guardar
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)

    print("✅ NCAA normalizado")
    print(f"📄 Archivo: {out_path}")
    print(f"🔢 Filas: {len(df)}")
    print("🧱 Columnas:")
    for c in df.columns:
        print(" -", c)


if __name__ == "__main__":
    main()
