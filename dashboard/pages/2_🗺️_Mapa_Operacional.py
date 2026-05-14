import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import folium
from streamlit_folium import st_folium

from dashboard.utils.db_queries import carregar_posicoes_recentes

st.set_page_config(page_title="Mapa Operacional", page_icon="🗺️", layout="wide")
st.title("🗺️ Mapa Operacional — Posições em Tempo Real")

minutos = st.slider("Janela de tempo (minutos atrás)", 5, 60, 15)

df = carregar_posicoes_recentes(minutos=minutos)

if df.empty:
    st.warning("Nenhuma posição disponível na janela selecionada.")
    st.stop()

st.caption(f"Exibindo {len(df):,} veículos nos últimos {minutos} minutos.")

m = folium.Map(
    location=[-23.55, -46.63],
    zoom_start=11,
    tiles="cartodbpositron",
)

for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row.latitude, row.longitude],
        radius=3,
        popup=f"Linha {row.codigo_linha} · Veículo {row.prefixo_veiculo}",
        tooltip=f"{row.codigo_linha}",
        color="#FF4B4B",
        fill=True,
        fill_opacity=0.7,
    ).add_to(m)

st_folium(m, width=1200, height=600)
