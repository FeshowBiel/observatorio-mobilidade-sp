import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.express as px

from utils.db_queries import carregar_pontualidade_diaria

st.set_page_config(page_title="Comparativo de Linhas", page_icon="📈", layout="wide")
st.title("📈 Comparativo entre Linhas")

df = carregar_pontualidade_diaria()

if df.empty:
    st.warning("Nenhum dado disponível ainda.")
    st.stop()

linhas = st.multiselect(
    "Selecione as linhas para comparar",
    options=sorted(df["letreiro"].dropna().unique()),
    default=df["letreiro"].dropna().unique()[:5].tolist(),
)

if not linhas:
    st.info("Selecione ao menos uma linha.")
    st.stop()

filtered = df[df["letreiro"].isin(linhas)]

col1, col2 = st.columns(2)

with col1:
    resumo = (
        filtered.groupby("letreiro")
        .agg(
            velocidade_media=("velocidade_media_kmh", "mean"),
            pontualidade_media=("pontualidade_pct", "mean"),
            total_viagens=("viagens_total", "sum"),
        )
        .reset_index()
    )
    fig = px.scatter(
        resumo,
        x="velocidade_media",
        y="pontualidade_media",
        size="total_viagens",
        text="letreiro",
        title="Velocidade média vs Pontualidade por linha",
        labels={
            "velocidade_media": "Velocidade média (km/h)",
            "pontualidade_media": "Pontualidade média (%)",
        },
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig2 = px.box(
        filtered,
        x="letreiro",
        y="velocidade_media_kmh",
        title="Distribuição de velocidade por linha",
        color="letreiro",
    )
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Dias úteis vs Fim de semana")
comp = (
    filtered.groupby(["letreiro", "eh_dia_util"])["velocidade_media_kmh"]
    .mean()
    .reset_index()
)
comp["tipo_dia"] = comp["eh_dia_util"].map({True: "Dia útil", False: "Fim de semana"})
fig3 = px.bar(
    comp,
    x="letreiro",
    y="velocidade_media_kmh",
    color="tipo_dia",
    barmode="group",
    title="Velocidade média: dia útil vs fim de semana",
)
st.plotly_chart(fig3, use_container_width=True)
