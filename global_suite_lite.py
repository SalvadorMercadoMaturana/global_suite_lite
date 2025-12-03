import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from streamlit_option_menu import option_menu

# ======================
#   ESTILO GLOBAL
# ======================
st.set_page_config(layout="wide")

st.markdown("""
<style>
    .block-container {padding-top: 1rem;}
    .small-text {font-size:13px; color:#888;}
    .big-number {font-size:40px; font-weight:600; margin-top:-10px;}
    .metric-card {
        background: #fff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        text-align:center;
    }
</style>
""", unsafe_allow_html=True)

# ======================
#   SIDEBAR
# ======================
with st.sidebar:
    selected = option_menu(
        menu_title="GlobalSuite Lite",
        options=["Inicio", "Análisis", "Planes", "Gestión", "Scorecard", "Auditoría"],
        icons=["house", "graph-up", "clipboard-check", "hammer", "bar-chart", "search"],
        menu_icon="shield-check",
        default_index=1,
    )

st.title("🔎 Análisis de Riesgos – Dashboard")

# ======================
#   BARRA DE FILTROS (NO AFECTA LA TABLA)
# ======================
st.subheader("Filtros de análisis")

col1, col2, col3, col4 = st.columns(4)
col1.selectbox("Análisis", ["Todos", "ISO 27005", "ISO 31000"])
col2.selectbox("Metodología", ["Todos", "Cualitativa", "Cuantitativa"])
col3.selectbox("Categoría", ["Todas", "TI", "Finanzas", "Operaciones"])
col4.selectbox("Dimensión", ["Todas", "Confidencialidad", "Integridad", "Disponibilidad"])

st.write("---")

# ======================
#   MATRIZ DE CALOR
# ======================
st.subheader("📊 Matriz Probabilidad x Impacto")

prob_labels = ["Muy bajo", "Bajo", "Medio", "Alto", "Muy alto"]
matrix = np.array([
    [2, 4, 8, 12, 18],
    [4, 8, 12, 16, 20],
    [6, 10, 14, 20, 24],
    [10, 14, 20, 26, 30],
    [12, 18, 24, 30, 36],
])

fig, ax = plt.subplots(figsize=(7, 4))
sns.heatmap(matrix, cmap="RdYlGn_r", annot=True, fmt="d",
            xticklabels=prob_labels, yticklabels=prob_labels,
            ax=ax)
st.pyplot(fig)

# ======================
#   CONTRASEÑA
# ======================
PASSWORD = "admin123"

if "auth" not in st.session_state:
    st.session_state.auth = False

def login():
    pwd = st.text_input("Ingrese contraseña:", type="password")
    if st.button("Acceder"):
        if pwd == PASSWORD:
            st.session_state.auth = True
        else:
            st.error("Contraseña incorrecta")

if not st.session_state.auth:
    st.title("🔐 Acceso restringido al dashboard")
    login()
    st.stop()

# ======================
#   CARGAR EXCEL
# ======================
st.write("---")
st.subheader("📋 Cargar matriz de riesgos")

file = st.file_uploader("📂 Subir Excel", type=["xlsx", "xls", "xlsm"])

if file is not None:
    try:
        df = pd.read_excel(file, engine="openpyxl")
        st.success("Archivo cargado correctamente")

        st.write("---")
        st.subheader("🎚 Segmentadores automáticos")

        filtered_df = df.copy()

        with st.expander("Mostrar / Ocultar filtros"):

            for col in df.columns:
                series = filtered_df[col]  # clave: siempre desde filtered_df

                # ================================================
                # 1) TEXTO / CATEGÓRICOS
                # ================================================
                if series.dtype == object or series.nunique() < 20:

                    unique_vals = list(series.dropna().unique())
                    unique_vals_str = sorted([str(v) for v in unique_vals])
                    val_map = {str(v): v for v in unique_vals}

                    selected_str = st.multiselect(
                        f"Filtrar {col}:",
                        unique_vals_str,
                        unique_vals_str
                    )

                    selected_real = [val_map[s] for s in selected_str]

                    filtered_df = filtered_df[filtered_df[col].isin(selected_real)]
                    continue

                # ================================================
                # 2) FECHAS
                # ================================================
                if np.issubdtype(series.dtype, np.datetime64):

                    min_date = series.min()
                    max_date = series.max()

                    date_tuple = st.date_input(
                        f"Rango de fechas para {col}:",
                        (min_date, max_date)
                    )

                    if isinstance(date_tuple, tuple):
                        start, end = date_tuple
                        filtered_df = filtered_df[
                            (series >= pd.to_datetime(start)) &
                            (series <= pd.to_datetime(end))
                        ]
                    continue

                # ================================================
                # 3) NUMÉRICOS
                # ================================================
                try:
                    min_val = float(series.min())
                    max_val = float(series.max())

                    sel_min, sel_max = st.slider(
                        f"Rango para {col}:",
                        min_val, max_val,
                        (min_val, max_val)
                    )

                    filtered_df = filtered_df[
                        (series >= sel_min) & (series <= sel_max)
                    ]
                    continue

                except:
                    # TIPOS MIXTOS — tratar como texto
                    unique_vals = list(series.dropna().unique())
                    unique_vals_str = sorted([str(v) for v in unique_vals])
                    val_map = {str(v): v for v in unique_vals}

                    selected_str = st.multiselect(
                        f"Filtrar {col}:",
                        unique_vals_str,
                        unique_vals_str
                    )

                    selected_real = [val_map[s] for s in selected_str]

                    filtered_df = filtered_df[filtered_df[col].isin(selected_real)]
                    continue

        # ======================
        #   SLIDER DE FILAS
        # ======================
        st.write("---")
        st.subheader("📌 Recorrer filas filtradas")

        total_rows = len(filtered_df)

        if total_rows == 0:
            st.warning("No hay filas para mostrar. Quita o modifica los filtros.")
        else:
            default_end = min(50, total_rows)

            row_start, row_end = st.slider(
                "Selecciona rango de filas:",
                0, total_rows,
                (0, default_end),
                step=1
            )

            if row_start == row_end:
                row_end = min(row_start + 1, total_rows)

            subset_df = filtered_df.iloc[row_start:row_end]

            st.dataframe(subset_df, use_container_width=True, height=450)

    except Exception as e:
        st.error("Error al procesar el archivo.")
        st.exception(e)

else:
    st.info("Sube un archivo Excel para comenzar.")
