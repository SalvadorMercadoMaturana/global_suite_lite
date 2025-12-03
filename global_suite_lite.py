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
#   SIDEBAR – ICONOS
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
#   BARRA DE FILTROS
# ======================
st.subheader("Filtros de análisis")

col1, col2, col3, col4 = st.columns(4)
anal = col1.selectbox("Análisis", ["Todos", "ISO 27005", "ISO 31000"])
metod = col2.selectbox("Metodología", ["Todos", "Cualitativa", "Cuantitativa"])
categoria = col3.selectbox("Categoría", ["Todas", "TI", "Finanzas", "Operaciones"])
dimension = col4.selectbox("Dimensión", ["Todas", "Confidencialidad", "Integridad", "Disponibilidad"])

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
#   CONTRASEÑA DE ACCESO
# ======================
PASSWORD = "admin123"   # cámbiala aquí

if "auth" not in st.session_state:
    st.session_state.auth = False

def login():
    pwd = st.text_input("Ingrese contraseña:", type="password")
    if st.button("Acceder"):
        if pwd == PASSWORD:
            st.session_state.auth = True
            st.success("Acceso concedido")
        else:
            st.error("Contraseña incorrecta")

if not st.session_state.auth:
    st.title("🔐 Acceso restringido al dashboard")
    login()
    st.stop()

# ======================
#   SECCIÓN DE TABLA + EXCEL
# ======================
st.write("---")
st.subheader("📋 Cargar matriz de riesgos")

file = st.file_uploader("📂 Subir Excel de riesgos", type=["xlsx", "xls"])

if file is not None:
    try:
        df = pd.read_excel(file)
        st.success("Archivo cargado correctamente")

        st.write("---")
        st.subheader("🎚 Segmentadores automáticos")

        filtered_df = df.copy()

        with st.expander("Mostrar / Ocultar filtros"):
            for col in df.columns:

                # Si la columna tiene pocos valores, multiselect
                if df[col].dtype == object or df[col].nunique() < 20:
                    vals = st.multiselect(
                        f"Filtrar {col}:",
                        df[col].dropna().unique(),
                        default=list(df[col].dropna().unique())
                    )
                    filtered_df = filtered_df[filtered_df[col].isin(vals)]

                else:
                    # Si es numérica: slider rango
                    min_val = float(df[col].min())
                    max_val = float(df[col].max())
                    sel_min, sel_max = st.slider(
                        f"Rango para {col}:",
                        min_val, max_val,
                        (min_val, max_val)
                    )
                    filtered_df = filtered_df[
                        (filtered_df[col] >= sel_min) &
                        (filtered_df[col] <= sel_max)
                    ]

        st.write("---")
        st.subheader("📊 Vista de tabla filtrada")

        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=400,
            hide_index=True
        )

    except Exception as e:
        st.error("Error al cargar el archivo. Verifique que sea un Excel válido.")
        st.exception(e)

else:
    st.info("Sube un archivo Excel para ver la tabla y los segmentadores.")

# ======================
#   KPI + GRÁFICOS
# ======================
colA, colB, colC = st.columns([1,1,1])

with colA:
    st.subheader("Supera NRA")
    st.markdown('<div class="metric-card"><div class="big-number">464</div><div class="small-text">de 1236</div></div>',
                unsafe_allow_html=True)

with colB:
    st.subheader("Distribución de Riesgos")
    pie = px.pie(values=[40, 25, 20, 10, 5],
                 names=["Muy alto","Alto","Medio","Bajo","Muy bajo"],
                 color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(pie, use_container_width=True)

with colC:
    st.subheader("Mapa de riesgo")
    tree = px.treemap(
        names=["Muy alto","Alto","Medio","Bajo","Muy bajo"],
        parents=["","", "", "", ""],
        values=[36,30,20,10,4],
        color=[5,4,3,2,1],
        color_continuous_scale="RdYlGn_r"
    )
    st.plotly_chart(tree, use_container_width=True)

# ======================
#   TABLA DE DATOS
# ======================
st.write("---")
st.subheader("📋 Resultados de análisis")

df_demo = pd.DataFrame({
    "Análisis": ["Ciberseguridad"]*8,
    "Elemento": ["AWS","App","Cita Previa","Aceso a Internet","Nóminas","Ciudadano","Operación","Banca Privada"],
    "Riesgo": ["A.11 Acceso no autorizado"]*8,
    "Nivel dimensión": ["Alto"]*8,
    "Nivel": ["Muy alto"]*8,
    "NRA": ["Medio"]*8
})

st.dataframe(df_demo, use_container_width=True, height=350)

