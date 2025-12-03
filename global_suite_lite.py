import streamlit as st
import pandas as pd

st.set_page_config(page_title="GlobalSuite Lite", layout="wide")

st.title("🌐 GlobalSuite Lite – MVP")

# ---- Sidebar ----
menu = st.sidebar.selectbox(
    "Módulo", 
    ["Dashboard", "Activos", "Riesgos", "Controles ISO 27001"]
)

# ---- Base de datos en memoria ----
if "activos" not in st.session_state:
    st.session_state.activos = pd.DataFrame(columns=["Nombre", "Tipo", "Valor"])

if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=["Riesgo", "Prob", "Impacto", "Nivel"])

if "controles" not in st.session_state:
    st.session_state.controles = pd.DataFrame({
        "Control": [
            "5.1 Políticas de seguridad",
            "5.2 Roles y responsabilidades",
            "8.1 Gestión de activos",
            "8.3 Gestión de medios removibles"
        ],
        "Implementado": [False, False, False, False]
    })

# ---- Dashboard ----
if menu == "Dashboard":
    st.header("📊 Dashboard general")

    col1,col2,col3 = st.columns(3)
    col1.metric("Activos", len(st.session_state.activos))
    col2.metric("Riesgos", len(st.session_state.riesgos))
    col3.metric("Controles", len(st.session_state.controles))

    if len(st.session_state.riesgos) > 0:
        st.subheader("Matriz de riesgo")
        st.dataframe(st.session_state.riesgos)

# ---- Activos ----
elif menu == "Activos":
    st.header("🗂 Gestión de activos")

    with st.form("nuevo_activo"):
        nombre = st.text_input("Nombre del activo")
        tipo = st.selectbox("Tipo", ["Información", "Hardware", "Persona", "Software"])
        valor = st.slider("Valor", 1, 5)
        submit = st.form_submit_button("Agregar")

    if submit:
        st.session_state.activos.loc[len(st.session_state.activos)] = [nombre, tipo, valor]
        st.success("Activo agregado correctamente")

    st.dataframe(st.session_state.activos)

# ---- Riesgos ----
elif menu == "Riesgos":
    st.header("⚠️ Gestión de riesgos")

    with st.form("nuevo_riesgo"):
        riesgo = st.text_input("Descripción del riesgo")
        prob = st.slider("Probabilidad", 1, 5)
        impacto = st.slider("Impacto", 1, 5)
        nivel = prob * impacto
        submit = st.form_submit_button("Agregar")

    if submit:
        st.session_state.riesgos.loc[len(st.session_state.riesgos)] = [riesgo, prob, impacto, nivel]
        st.success("Riesgo agregado")

    st.dataframe(st.session_state.riesgos)

# ---- Controles ----
elif menu == "Controles ISO 27001":
    st.header("🛡️ Controles ISO 27001 (Lite)")

    controles = st.session_state.controles

    for i in range(len(controles)):
        controles.at[i, "Implementado"] = st.checkbox(
            label=controles.at[i, "Control"],
            value=controles.at[i, "Implementado"]
        )

    st.dataframe(controles)
