import pandas as pd

# Cargar el archivo combinado
df = pd.read_csv('data_raw/wnba/wnba_combined.csv')

# --- Normalizar la carrera del jugador --- 
# Calcular la temporada de debut (año de la primera temporada del jugador)
rookie = (
    df.dropna(subset=["season"])  # Asegurarse de que 'year' no es nulo
    .groupby("player", as_index=False)["season"]
    .min()
    .rename(columns={"season": "rookie_season_start_year"})
)

# Unir la temporada de debut con los datos
df = df.merge(rookie, on="player", how="left")

# Calcular el año de carrera (1 = rookie, 2 = segunda temporada, etc.)
df["career_year"] = df["season"] - df["rookie_season_start_year"] + 1
df.loc[df["career_year"] < 1, "career_year"] = pd.NA  # Seguridad: eliminar valores negativos

# --- Filtrar columnas que no queremos o que no contienen valores válidos ---
df = df.dropna(subset=["career_year"])

# Guardar el archivo con los datos normalizados
df.to_csv('data_raw/wnba/wnba_normalized.csv', index=False)

# Mostrar mensaje de éxito
print("Datos normalizados guardados en: data_raw/wnba/wnba_normalized.csv")

