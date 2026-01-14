import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_master

st.set_page_config(page_title="Explorador", layout="wide")
st.title("🔎 Explorador de stats por temporada")

df = load_master()

# Sidebar filters
st.sidebar.header("Filtros")

lg = st.sidebar.multiselect("Liga (lg)", sorted(df["lg"].dropna().unique().tolist()), default=["NBA"] if "NBA" in df["lg"].unique() else None)

min_year = int(df["season_start_year"].min())
max_year = int(df["season_start_year"].max())
year_range = st.sidebar.slider("Rango de temporadas (año inicio)", min_year, max_year, (2000, max_year))

teams = sorted(df["team"].dropna().unique().tolist())
team_sel = st.sidebar.multiselect("Equipo (team)", teams, default=[])

pos_list = sorted(df["pos"].dropna().unique().tolist())
pos_sel = st.sidebar.multiselect("Posición (pos)", pos_list, default=[])

min_games = st.sidebar.slider("Mínimo partidos (g)", 0, int(df["g"].max()), 20)

# Número de jugadores en el top
top_n = st.sidebar.slider("Número de jugadores en el top", 1, 50, 20)

metric = st.sidebar.selectbox(
    "Métrica principal",
    ["pts_per_game", "ast_per_game", "trb_per_game", "mp_per_game", "fg_percent", "x3p_percent", "ft_percent"]
)

# Select second metric
secondary_metric = st.sidebar.selectbox(
    "Métrica secundaria",
    ["No seleccionar", "pts_per_game", "ast_per_game", "trb_per_game", "mp_per_game", "fg_percent", "x3p_percent", "ft_percent"]
)

# Apply filters
f = df.copy()
if lg:
    f = f[f["lg"].isin(lg)]
f = f[(f["season_start_year"] >= year_range[0]) & (f["season_start_year"] <= year_range[1])]
if team_sel:
    f = f[f["team"].isin(team_sel)]
if pos_sel:
    f = f[f["pos"].isin(pos_sel)]
f = f[f["g"] >= min_games]

# KPIs
c1, c2, c3 = st.columns(3)
c1.metric("Filas filtradas", f"{len(f):,}".replace(",", "."))
c2.metric("Jugadores únicos", f"{f['player_id'].nunique():,}".replace(",", "."))
c3.metric("Temporadas", f"{int(f['season_start_year'].min())}–{int(f['season_start_year'].max())}" if len(f) else "-")

st.divider()

# Top players by selected metric (for a chosen season)
season_pick = st.selectbox("Temporada (stats)", sorted(f["season"].dropna().unique().tolist())[::-1] if len(f) else [])
if season_pick:
    fs = f[f["season"] == season_pick].copy()
    top = fs.sort_values(metric, ascending=False).head(top_n)

    st.subheader(f"Top {top_n} — {metric} — {season_pick}")
    
    # Create a stacked bar chart if a secondary metric is selected
    if secondary_metric != "No seleccionar":
        # Create a new dataframe for the stacked bars
        stacked_data = top[["player_name", metric, secondary_metric]].copy()
        
        # Convert the dataframe from wide to long format for Plotly
        stacked_data = stacked_data.melt(id_vars="player_name", value_vars=[metric, secondary_metric], 
                                         var_name="metric", value_name="value")

        # Calculate the total value for each player (sum of the metrics)
        stacked_data["total_value"] = stacked_data.groupby("player_name")["value"].transform("sum")

        # Order the players by the total value
        stacked_data = stacked_data.sort_values("total_value", ascending=False)

        # Create the stacked bar chart
        fig = px.bar(stacked_data,
                     x="player_name",
                     y="value",
                     color="metric",  # Different colors for each metric
                     title=f"Top {top_n} — {metric} y {secondary_metric} — {season_pick}",
                     labels={"value": "Valor", "player_name": "Jugador"},
                     color_discrete_map={metric: "blue", secondary_metric: "orange"},  # Use distinct colors for each metric
                     text="value")  # Show the value on top of bars
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Standard bar chart with just the main metric
        fig = px.bar(top, x="player_name", y=metric, hover_data=["team", "pos", "g"], title="")
        st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Tabla (ordenable)")
cols_show = ["season","lg","player_name","team","pos","age","g","mp_per_game","pts_per_game","trb_per_game","ast_per_game","fg_percent","x3p_percent","ft_percent","draft_year","draft_round","draft_pick","draft_team","college","season_start_year"]
cols_show = [c for c in cols_show if c in f.columns]
st.dataframe(f[cols_show].sort_values(["season_start_year","pts_per_game"], ascending=[False, False]), use_container_width=True)
