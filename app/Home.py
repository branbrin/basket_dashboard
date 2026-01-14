import streamlit as st
from utils import load_master

st.set_page_config(page_title="NBA Histórico Dashboard", layout="wide")

# En la página Home de Streamlit
st.title(" Explorador de Estadísticas NBA, WNBA y NCAA")

st.markdown("""
¡Bienvenido al **Explorador de estadísticas** de baloncesto! Aquí podrás explorar y comparar las estadísticas de jugadores de tres de las ligas más importantes de baloncesto: **NBA**, **WNBA** y **NCAA**.

### ¿Qué puedes hacer?
1. **Explorar estadísticas por temporada**:
   - Filtra los jugadores por año, equipo, posición y métrica.
   - Visualiza las estadísticas de jugadores top para cada temporada seleccionada.
   - **Gráficos interactivos**: Compara la evolución de las métricas más relevantes como puntos, asistencias, rebotes, etc.

2. **Exploración por Draft**:
   - Analiza los jugadores seleccionados en diferentes años de draft.
   - Compara la evolución de sus métricas a lo largo de las temporadas.
   - **Compara jugadores**: Selecciona varios jugadores y compáralos en gráficos para ver cómo se desarrollaron en diferentes equipos.

3. **Análisis de Jugadores**:
   - Accede a estadísticas individuales de los jugadores.
   - Compara las trayectorias de distintos jugadores de NBA, WNBA y NCAA.

### Fuentes de los datos:
- **NBA**: La información sobre la NBA proviene de la API de [Sumitro Datta](https://www.kaggle.com/sumitrodatta) que contiene estadísticas históricas de jugadores de la NBA.
- **WNBA**: Las estadísticas de la WNBA fueron extraídas de [Basketball Reference](https://www.basketball-reference.com) y normalizadas para hacer comparaciones entre temporadas.
- **NCAA**: Los datos de NCAA fueron obtenidos desde un [dataset de Kaggle](https://www.kaggle.com) que contiene estadísticas completas de los jugadores universitarios, con lo que podrás comparar jugadores de diferentes años.

¡Explora las métricas, filtra los jugadores y empieza a analizar sus trayectorias! 
""")
