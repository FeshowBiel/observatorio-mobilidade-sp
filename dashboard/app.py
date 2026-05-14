import streamlit as st

st.set_page_config(
    page_title="Observatório de Mobilidade SP",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🚌 Observatório de Mobilidade Urbana de São Paulo")
st.markdown("""
Plataforma analítica pública de pontualidade, fluxo e impacto climático
no transporte coletivo da cidade de São Paulo.

**Fontes:** API Olho Vivo (SPTrans) · Open-Meteo · GeoSampa
""")

st.divider()

from dashboard.utils.db_queries import get_summary_metrics

metrics = get_summary_metrics()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Linhas monitoradas",   metrics.get("linhas",    "—"))
col2.metric("Veículos únicos",      metrics.get("veiculos",  "—"))
col3.metric("Posições coletadas",   metrics.get("posicoes",  "—"))
col4.metric("Última atualização",   metrics.get("ultima_at", "—"))

st.info(
    "Use a navegação à esquerda para explorar as análises por tema.",
    icon="ℹ️",
)
