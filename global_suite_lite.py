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
        "GlobalSuite Lite",
        ["Inicio", "Análisis", "Planes", "Gestión", "Scorecard", "Auditoría"],
        icons=["house", "graph-up", "clipboard-check", "hammer", "bar-chart", "search"],
        menu_icon="shield-check",
        default_index=1,
    )

st.title("🔎 Análisis de Riesgos – Dashboard")

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
            xticklabels=prob_labels, yticklabels=prob_labels, ax=ax)
st.pyplot(fig)

# ======================
#   CONTRASEÑA
# ======================
PASSWORD = "admin123"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    pwd = st.text_input("Ingrese contraseña:", type="password")
    if st.button("Acceder"):
        if pwd == PASSWORD:
            st.session_state.auth = True
        else:
            st.error("Contraseña incorrecta")
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

        # ============================
        # NORMALIZAR TIPOS PARA QUE NO PETE
        # ============================
        for col in df.columns:
            # convertir fechas si se puede
            try:
                df[col] = pd.to_datetime(df[col], errors="ignore")
            except:
                pass

        st.write("---")
        st.subheader("🎚 Segmentadores automáticos (modo PowerBI)")

        user_filters = {}  # buffer de filtros

        # ============================
        # 1) CREAR WIDGETS SIN FILTRAR
        # ============================
        with st.expander("Mostrar / Ocultar filtros"):
            for col in df.columns:
                col_series = df[col]

                # ----- FECHAS -----
                if np.issubdtype(col_series.dtype, np.datetime64):
                    min_d, max_d = col_series.min(), col_series.max()
                    date_range = st.date_input(f"{col} (fecha):", (min_d, max_d))
                    user_filters[col] = ("date", date_range)
                    continue

                # ----- NUMÉRICOS REALES -----
                if np.issubdtype(col_series.dtype, np.number) and col_series.notna().all():
                    min_v, max_v = float(col_series.min()), float(col_series.max())
                    sel_min, sel_max = st.slider(
                        f"{col} (num):", min_v, max_v, (min_v, max_v)
                    )
                    user_filters[col] = ("numeric", (sel_min, sel_max))
                    continue

                # ----- TEXTO / MIXTOS -----
                unique_vals = sorted(col_series.dropna().astype(str).unique())
                selected = st.multiselect(f"{col} (texto):", unique_vals, unique_vals)
                user_filters[col] = ("text", selected)

        # ============================
        # 2) APLICAR FILTROS EN UN SOLO PASO
        # ============================
        filtered_df = df.copy()

        for col, (ftype, filt) in user_filters.items():
            series = filtered_df[col]

            if ftype == "text":
                filtered_df = filtered_df[series.astype(str).isin(filt)]

            elif ftype == "numeric":
                lo, hi = filt
                filtered_df = filtered_df[(series >= lo) & (series <= hi)]

            elif ftype == "date":
                start, end = filt
                start, end = pd.to_datetime(start), pd.to_datetime(end)
                filtered_df = filtered_df[(series >= start) & (series <= end)]

        # ============================
        # 3) SLIDER PARA RECORRER FILAS
        # ============================
        st.write("---")
        st.subheader("📌 Recorrer filas filtradas")

        total = len(filtered_df)

        if total == 0:
            st.error("❌ No se encontraron filas con los filtros seleccionados.")
        else:
            end_default = min(50, total)
            a, b = st.slider("Rango de filas:", 0, total, (0, end_default))

            if a == b:
                b = min(a + 1, total)

            st.dataframe(filtered_df.iloc[a:b], use_container_width=True, height=450)

    except Exception as e:
        st.error("Error al procesar el Excel")
        st.exception(e)

else:
    st.info("Sube el archivo Excel para comenzar.")
