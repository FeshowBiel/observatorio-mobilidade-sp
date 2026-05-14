import streamlit as st
import plotly.express as px

from dashboard.utils.db_queries import carregar_pontualidade_diaria

st.set_page_config(page_title="Visão Geral", page_icon="📊", layout="wide")
st.title("📊 Visão Geral — Pontualidade por Linha")

df = carregar_pontualidade_diaria()

if df.empty:
    st.warning("Nenhum dado disponível ainda. Aguarde a coleta acumular dados.")
    st.stop()

# Filtros
col1, col2 = st.columns(2)
with col1:
    linhas = st.multiselect(
        "Filtrar linhas",
        options=sorted(df["letreiro"].dropna().unique()),
        default=[],
    )
with col2:
    apenas_uteis = st.checkbox("Apenas dias úteis", value=False)

filtered = df.copy()
if linhas:
    filtered = filtered[filtered["letreiro"].isin(linhas)]
if apenas_uteis:
    filtered = filtered[filtered["eh_dia_util"]]

# Gráfico de pontualidade
fig = px.line(
    filtered.sort_values("data"),
    x="data",
    y="pontualidade_pct",
    color="letreiro",
    title="Pontualidade diária por linha (%)",
    labels={"pontualidade_pct": "Pontualidade (%)", "data": "Data"},
)
st.plotly_chart(fig, use_container_width=True)

# Top 10 linhas por velocidade média
top = (
    filtered.groupby("letreiro")["velocidade_media_kmh"]
    .mean()
    .reset_index()
    .sort_values("velocidade_media_kmh", ascending=True)
    .tail(10)
)
fig2 = px.bar(
    top,
    x="velocidade_media_kmh",
    y="letreiro",
    orientation="h",
    title="Top 10 linhas — velocidade média (km/h)",
)
st.plotly_chart(fig2, use_container_width=True)

st.dataframe(filtered, use_container_width=True)
