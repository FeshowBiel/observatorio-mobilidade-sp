"""Queries para o dashboard, com cache."""
import os
from pathlib import Path

from dotenv import load_dotenv
# Carrega .env do root do projeto (dois níveis acima de utils/)
load_dotenv(Path(__file__).parent.parent.parent / ".env")

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

_DATABASE_URL: str | None = None


def _get_database_url() -> str:
    global _DATABASE_URL
    if _DATABASE_URL:
        return _DATABASE_URL
    url = os.getenv("DATABASE_URL")
    if not url:
        try:
            url = st.secrets["DATABASE_URL"]
        except Exception:
            pass
    if not url:
        raise RuntimeError("DATABASE_URL não configurado")
    _DATABASE_URL = url
    return url


@st.cache_resource
def get_engine():
    return create_engine(_get_database_url(), pool_pre_ping=True)


@st.cache_data(ttl=300)
def get_summary_metrics() -> dict:
    try:
        with get_engine().connect() as conn:
            result = conn.execute(text("""
                select
                    (select count(distinct codigo_linha) from marts.fct_posicoes)  as linhas,
                    (select count(distinct prefixo_veiculo) from marts.fct_posicoes) as veiculos,
                    (select count(*) from marts.fct_posicoes)                       as posicoes,
                    (select max(coletado_em)::text from marts.fct_posicoes)         as ultima_at
            """)).mappings().one()
        return dict(result)
    except Exception:
        return {}


@st.cache_data(ttl=300)
def carregar_pontualidade_diaria() -> pd.DataFrame:
    query = """
        select
            data,
            codigo_linha,
            letreiro,
            denominacao_terminal_principal,
            viagens_total,
            pontualidade_pct,
            velocidade_media_kmh,
            eh_dia_util,
            estacao
        from marts.mart_pontualidade_diaria
        where data >= current_date - interval '30 days'
        order by data desc
    """
    return pd.read_sql(query, get_engine())


@st.cache_data(ttl=300)
def carregar_correlacao_clima() -> pd.DataFrame:
    query = """
        select *
        from marts.mart_correlacao_clima
        order by hora_truncada desc
        limit 2000
    """
    return pd.read_sql(query, get_engine())


@st.cache_data(ttl=60)
def carregar_posicoes_recentes(minutos: int = 15) -> pd.DataFrame:
    # Tenta janela solicitada; se vazia, pega o snapshot mais recente disponível
    query = f"""
        with ultima_coleta as (
            select max(coletado_em) as ts from marts.fct_posicoes
        ),
        janela as (
            select coletado_em from marts.fct_posicoes
            where coletado_em >= now() - interval '{minutos} minutes'
            limit 1
        )
        select latitude, longitude, codigo_linha, prefixo_veiculo,
               hora_referencia, coletado_em
        from marts.fct_posicoes
        where
            -- se há dados na janela solicitada, usa ela
            case when (select count(*) from janela) > 0
                 then coletado_em >= now() - interval '{minutos} minutes'
            -- senão, pega o snapshot mais recente disponível
                 else coletado_em = (select ts from ultima_coleta)
            end
        limit 5000
    """
    return pd.read_sql(query, get_engine())
