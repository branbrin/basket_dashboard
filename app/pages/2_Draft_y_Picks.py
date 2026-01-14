import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_master

st.set_page_config(page_title="Draft y Picks", layout="wide")
st.title("🎯 Draft y Picks")

# Cargar los datos
df = load_master()  # dataframe completo (NO filtrado)
f = df.copy()       # copia para filtros de tabla 2

# --- Métricas disponibles y nombres bonitos ---
METRICS = {
    "PTS (puntos/partido)": ("pts_per_game", "PTS / partido"),
    "AST (asistencias/partido)": ("ast_per_game", "AST / partido"),
    "TRB (rebotes/partido)": ("trb_per_game", "REB / partido"),
    "MP (minutos/partido)": ("mp_per_game", "MIN / partido"),
    "FG% (tiro de campo)": ("fg_percent", "FG%"),
    "FT% (tiro libre)": ("ft_percent", "FT%"),
    "3P% (triple)": ("x3p_percent", "3P%"),  # si existe en tu dataset (en el Kaggle sí)
}

# Si alguna columna no existe (por cambios de dataset), filtramos automáticamente:
METRICS = {k: v for k, v in METRICS.items() if v[0] in df.columns}

X_OPTIONS = {
    "Por temporada": ("season_start_year", "Año de temporada"),
    "Por edad": ("age", "Edad"),
    "Temporada normalizada (desde rookie)": ("career_year", "Año de carrera (1 = rookie)"),
}



# Asegura que season_start_year existe (si no, lo calculas desde season)
if "season_start_year" not in df.columns and "season" in df.columns:
    # "2018-19" -> 2018
    df["season_start_year"] = pd.to_numeric(df["season"].astype(str).str.slice(0, 4), errors="coerce")

# --- Build normalized career year (Year 1, 2, 3...) ---
# Compute rookie season as first season_start_year present in the dataset for each player
rookie = (
    df.dropna(subset=["season_start_year"])
      .groupby("player_name", as_index=False)["season_start_year"]
      .min()
      .rename(columns={"season_start_year": "rookie_season_start_year"})
)

# Comprobar si existe la columna rookie_season_start_year
if "rookie_season_start_year" not in df.columns:
    # Solo para NBA, ya que NCAA y WNBA no tienen esa columna
    if "nba" in df["lg"].unique():
        rookie = (
            df.dropna(subset=["season_start_year"])
            .groupby("player_name", as_index=False)["season_start_year"]
            .min()
            .rename(columns={"season_start_year": "rookie_season_start_year"})
        )
        df = df.merge(rookie, on="player_name", how="left")

# Ahora puedes calcular la columna career_year
df["career_year"] = df["season_start_year"] - df["rookie_season_start_year"] + 1
df.loc[df["career_year"] < 1, "career_year"] = pd.NA  # Safety



# Sidebar filters
min_dy = int(pd.to_numeric(df["draft_year"], errors="coerce").min())
max_dy = int(pd.to_numeric(df["draft_year"], errors="coerce").max())
draft_year_range = st.sidebar.slider("Rango de año de draft", min_dy, max_dy, (2000, max_dy))

pick_value = st.sidebar.number_input("Pick overall (ej. 1)", min_value=1, max_value=200, value=1, step=1)

# Selector de año encima de la tabla 1
selected_draft_year = st.selectbox("Seleccionar año de draft", range(min_dy, max_dy + 1), key="year_select")

# Tabla 1: jugadores drafteados ese año (usa df completo)
filtros_draft_year = df[df["draft_year"] == selected_draft_year]

# Tabla 2: filtras f para pick + rango
f = f[(f["draft_year"] >= draft_year_range[0]) & (f["draft_year"] <= draft_year_range[1])]
f = f[f["draft_pick"] == pick_value]

# --------------------
# TABLA 1 + GRÁFICA 1
# --------------------
st.subheader(f"Jugadores drafteados en {selected_draft_year}")
if len(filtros_draft_year) == 0:
    st.warning(f"No hay jugadores drafteados en {selected_draft_year}.")
else:
    filtros_draft_year_unique = filtros_draft_year.drop_duplicates(subset=["player_name"])
    st.dataframe(
        filtros_draft_year_unique[["player_name", "team", "draft_pick", "draft_team", "college"]],
        use_container_width=True
    )

    st.subheader("Evolución de los jugadores seleccionados")

    selected_players_1 = st.multiselect(
        "Seleccionar jugadores para comparar en la Gráfica 1",
        filtros_draft_year_unique["player_name"].unique(),
        key="players_graph_1"
    )

    # Selector de eje X
    x_mode_1 = st.radio(
        "Eje X (Gráfica 1)",
        list(X_OPTIONS.keys()),
        horizontal=True,
        key="xmode_graph_1",
    )



    # Selector de métrica (bonita)
    metric_label_1 = st.selectbox(
        "Métrica (Gráfica 1)",
        list(METRICS.keys()),
        key="metric_graph_1",
    )
    metric_1, metric_y_label_1 = METRICS[metric_label_1]
    x_col_1, x_label_1 = X_OPTIONS[x_mode_1]

    max_career_year = None
    if x_col_1 == "career_year":
        max_career_year = st.slider("Limitar a los primeros N años de carrera (Gráfica 1)", 3, 25, 15, key="cy_lim_1")

    if selected_players_1:
        selected_data_1 = df[df["player_name"].isin(selected_players_1)].copy()

        # Filtrar nulos en X e Y
        selected_data_1 = selected_data_1[selected_data_1[metric_1].notna() & selected_data_1[x_col_1].notna()]

        if max_career_year is not None:
            selected_data_1 = selected_data_1[selected_data_1["career_year"] <= max_career_year]

        # Ordenar para que líneas salgan bien (sobre todo por edad)
        selected_data_1 = selected_data_1.sort_values([ "player_name", x_col_1 ])

        if len(selected_data_1) > 0:
            fig_1 = px.line(
                selected_data_1,
                x=x_col_1,
                y=metric_1,
                color="player_name",
                markers=True,
                title=f"{metric_label_1} — ({', '.join(selected_players_1)})",
                labels={x_col_1: x_label_1, metric_1: metric_y_label_1},
            )

            # Opcional: que el eje X sea entero si es temporada
            if x_col_1 == "season_start_year":
                fig_1.update_xaxes(dtick=1)

            # Opcional: formato % para porcentajes
            if metric_1.endswith("_percent"):
                fig_1.update_yaxes(tickformat=".0%")

            st.plotly_chart(fig_1, use_container_width=True, key="graph_1")
        else:
            st.warning("No hay datos disponibles (revisa eje X o métrica).")
    else:
        st.warning("Selecciona al menos un jugador para ver la evolución en la Gráfica 1.")

# --------------------
# TABLA 2 + GRÁFICA 2
# --------------------
st.subheader(f"Jugadores seleccionados con el pick #{pick_value} en el rango de años {draft_year_range[0]} - {draft_year_range[1]}")
if len(f) == 0:
    st.warning(f"No hay jugadores con el pick #{pick_value} en ese rango de años.")
else:
    f_unique = f.drop_duplicates(subset=["player_name"])
    st.dataframe(
        f_unique[["player_name", "draft_year", "draft_team", "college", "draft_pick"]],
        use_container_width=True
    )

    st.subheader("Evolución de los jugadores seleccionados con el pick determinado")

    selected_players_2 = st.multiselect(
        "Seleccionar jugadores para comparar en la Gráfica 2",
        f_unique["player_name"].unique(),
        key="players_graph_2"
    )

    # Selector de eje X
    x_mode_2 = st.radio(
        "Eje X (Gráfica 2)",
        list(X_OPTIONS.keys()),
        horizontal=True,
        key="xmode_graph_2",
    )

    metric_label_2 = st.selectbox(
        "Métrica (Gráfica 2)",
        list(METRICS.keys()),
        key="metric_graph_2",
    )
    metric_2, metric_y_label_2 = METRICS[metric_label_2]
    x_col_2, x_label_2 = X_OPTIONS[x_mode_2]

    max_career_year = None
    if x_col_2 == "career_year":
        max_career_year = st.slider("Limitar a los primeros N años de carrera (Gráfica 1)", 3, 25, 15, key="cy_lim_2")

    if selected_players_2:
        selected_data_2 = df[df["player_name"].isin(selected_players_2)].copy()
        selected_data_2 = selected_data_2[selected_data_2[metric_2].notna() & selected_data_2[x_col_2].notna()]

        if max_career_year is not None:
            selected_data_2 = selected_data_2[selected_data_2["career_year"] <= max_career_year]

        selected_data_2 = selected_data_2.sort_values(["player_name", x_col_2])

        if len(selected_data_2) > 0:
            fig_2 = px.line(
                selected_data_2,
                x=x_col_2,
                y=metric_2,
                color="player_name",
                markers=True,
                title=f"{metric_label_2} — ({', '.join(selected_players_2)})",
                labels={x_col_2: x_label_2, metric_2: metric_y_label_2},
            )

            if x_col_2 == "season_start_year":
                fig_2.update_xaxes(dtick=1)

            if metric_2.endswith("_percent"):
                fig_2.update_yaxes(tickformat=".0%")

            st.plotly_chart(fig_2, use_container_width=True, key="graph_2")
        else:
            st.warning("No hay datos disponibles (revisa eje X o métrica).")
    else:
        st.warning("Selecciona al menos un jugador para ver la evolución en la Gráfica 2.")