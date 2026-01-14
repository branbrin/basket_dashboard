import streamlit as st
import plotly.express as px
from utils import load_master

st.set_page_config(page_title="Jugador", layout="wide")
st.title("👤 Perfil de jugador")

df = load_master()

# Player selector
players = df[["player_id","player_name"]].drop_duplicates().sort_values("player_name")
player_name = st.selectbox("Selecciona jugador", players["player_name"].tolist())

p = df[df["player_name"] == player_name].copy().sort_values("season_start_year")

# Header info
info = p[["player_id","player_name","draft_year","draft_round","draft_pick","draft_team","college"]].drop_duplicates().head(1)
st.dataframe(info, use_container_width=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Temporadas", str(p["season"].nunique()))
c2.metric("PTS media", f"{p['pts_per_game'].mean():.2f}")
c3.metric("AST media", f"{p['ast_per_game'].mean():.2f}")
c4.metric("REB media", f"{p['trb_per_game'].mean():.2f}")

st.divider()

metric = st.selectbox("Métrica para evolución", ["pts_per_game","ast_per_game","trb_per_game","mp_per_game","fg_percent","x3p_percent","ft_percent"])
fig = px.line(p, x="season_start_year", y=metric, markers=True, hover_data=["team","season","pos","g"])
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Tabla por temporada")
cols = ["season","lg","team","pos","age","g","gs","mp_per_game","pts_per_game","trb_per_game","ast_per_game","fg_percent","x3p_percent","ft_percent"]
st.dataframe(p[cols], use_container_width=True)
