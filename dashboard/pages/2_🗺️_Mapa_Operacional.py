import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime, timezone

from utils.db_queries import carregar_posicoes_recentes

st.set_page_config(page_title="Mapa Operacional", page_icon="🗺️", layout="wide")
st.title("🗺️ Mapa Operacional — Posições dos Ônibus")

minutos = st.slider("Janela de tempo (minutos atrás)", 5, 60, 15)

df = carregar_posicoes_recentes(minutos=minutos)

if df.empty:
    st.warning("Nenhuma posição disponível.")
    st.stop()

# Verifica se os dados são em tempo real ou o snapshot mais recente
agora = datetime.now(timezone.utc)
ts_dados = df["coletado_em"].max()
if hasattr(ts_dados, "tzinfo") and ts_dados.tzinfo is None:
    import pandas as pd
    ts_dados = ts_dados.tz_localize("UTC")

diff_min = (agora - ts_dados).total_seconds() / 60

if diff_min > minutos + 1:
    st.info(
        f"⚠️ Dados em tempo real indisponíveis (token SPTrans pendente). "
        f"Exibindo o snapshot mais recente: **{ts_dados.strftime('%d/%m/%Y %H:%M')} UTC** "
        f"({int(diff_min // 60)}h{int(diff_min % 60):02d}min atrás).",
        icon="📡",
    )
else:
    st.success(f"Dados ao vivo — última atualização: {ts_dados.strftime('%H:%M')} UTC")

st.caption(f"Exibindo **{len(df):,}** posições de {df['codigo_linha'].nunique()} linhas")

# Mapa
m = folium.Map(
    location=[-23.55, -46.63],
    zoom_start=11,
    tiles="cartodbpositron",
)

# Cores por linha para diferenciar visualmente
cores = ["#FF4B4B", "#FF8C00", "#1E90FF", "#32CD32", "#9932CC",
         "#FF1493", "#00CED1", "#FFD700", "#FF6347", "#00FA9A",
         "#4169E1", "#DC143C"]
linhas_unicas = df["codigo_linha"].unique()
cor_por_linha = {cl: cores[i % len(cores)] for i, cl in enumerate(linhas_unicas)}

for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row.latitude, row.longitude],
        radius=4,
        popup=f"<b>Linha {row.codigo_linha}</b><br>Veículo: {row.prefixo_veiculo}",
        tooltip=f"Linha {row.codigo_linha}",
        color=cor_por_linha.get(row.codigo_linha, "#FF4B4B"),
        fill=True,
        fill_opacity=0.8,
        weight=1,
    ).add_to(m)

st_folium(m, width=None, height=580, use_container_width=True)
