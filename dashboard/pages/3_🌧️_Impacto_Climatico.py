import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from dashboard.utils.db_queries import carregar_correlacao_clima

st.set_page_config(page_title="Impacto Climático", page_icon="🌧️", layout="wide")
st.title("🌧️ Impacto Climático na Velocidade")

df = carregar_correlacao_clima()

if df.empty:
    st.warning("Nenhum dado de correlação disponível ainda.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    fig = px.scatter(
        df,
        x="precipitacao_mm",
        y="velocidade_media_kmh",
        color="categoria_chuva",
        opacity=0.5,
        title="Precipitação vs Velocidade média",
        labels={
            "precipitacao_mm": "Precipitação (mm/h)",
            "velocidade_media_kmh": "Velocidade (km/h)",
        },
        trendline="ols",
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    box_df = df.groupby("categoria_chuva")["velocidade_media_kmh"].apply(list).reset_index()
    fig2 = px.box(
        df,
        x="categoria_chuva",
        y="velocidade_media_kmh",
        title="Distribuição de velocidade por categoria de chuva",
        category_orders={
            "categoria_chuva": ["sem_chuva", "chuva_fraca", "chuva_moderada", "chuva_forte"]
        },
    )
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Velocidade média por hora do dia")
df["hora"] = df["hora_truncada"].dt.hour
por_hora = df.groupby(["hora", "categoria_chuva"])["velocidade_media_kmh"].mean().reset_index()
fig3 = px.line(
    por_hora,
    x="hora",
    y="velocidade_media_kmh",
    color="categoria_chuva",
    title="Velocidade por hora do dia x condição de chuva",
)
st.plotly_chart(fig3, use_container_width=True)
