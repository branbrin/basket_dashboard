import pandas as pd
import os

# Directorio donde tienes los archivos CSV
folder_path = "data_raw/wnba"  # Cambia esta ruta a la carpeta donde están tus CSVs
output_file = "data_raw/wnba/wnba_combined.csv"  # Ruta de salida para el archivo combinado

# Crear una lista de todos los archivos CSV en la carpeta
files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# Lista para almacenar DataFrames
data_frames = []

# Leer cada archivo CSV y añadirlo a la lista
for file in files:
    file_path = os.path.join(folder_path, file)
    df = pd.read_csv(file_path)
    
    # Añadir una columna con el año basado en el nombre del archivo
    season = file.split('.')[0]  # El nombre del archivo sin la extensión
    df['year'] = season
    
    # Añadir el DataFrame a la lista
    data_frames.append(df)

# Concatenar todos los DataFrames en uno solo
wnba_df = pd.concat(data_frames, ignore_index=True)

# Asegurarnos de que las columnas sean del tipo adecuado
# Convertimos las columnas relevantes a tipos numéricos
wnba_df["G"] = pd.to_numeric(wnba_df["G"], errors='coerce')
wnba_df["GS"] = pd.to_numeric(wnba_df["GS"], errors='coerce')
wnba_df["MP"] = pd.to_numeric(wnba_df["MP"], errors='coerce')
wnba_df["FG"] = pd.to_numeric(wnba_df["FG"], errors='coerce')
wnba_df["FGA"] = pd.to_numeric(wnba_df["FGA"], errors='coerce')
wnba_df["3P"] = pd.to_numeric(wnba_df["3P"], errors='coerce')
wnba_df["3PA"] = pd.to_numeric(wnba_df["3PA"], errors='coerce')
wnba_df["FT"] = pd.to_numeric(wnba_df["FT"], errors='coerce')
wnba_df["FTA"] = pd.to_numeric(wnba_df["FTA"], errors='coerce')
wnba_df["ORB"] = pd.to_numeric(wnba_df["ORB"], errors='coerce')
wnba_df["TRB"] = pd.to_numeric(wnba_df["TRB"], errors='coerce')
wnba_df["AST"] = pd.to_numeric(wnba_df["AST"], errors='coerce')
wnba_df["STL"] = pd.to_numeric(wnba_df["STL"], errors='coerce')
wnba_df["BLK"] = pd.to_numeric(wnba_df["BLK"], errors='coerce')
wnba_df["TOV"] = pd.to_numeric(wnba_df["TOV"], errors='coerce')
wnba_df["PF"] = pd.to_numeric(wnba_df["PF"], errors='coerce')
wnba_df["PTS"] = pd.to_numeric(wnba_df["PTS"], errors='coerce')

# Guardar el archivo combinado y normalizado
wnba_df.to_csv(output_file, index=False)

# Mostrar mensaje de éxito
print(f"Archivo combinado guardado en: {output_file}")
