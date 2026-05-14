{{ config(materialized='table') }}

with viagens_hora as (
    select
        date_trunc('hour', hora_referencia) as hora_truncada,
        codigo_linha,
        avg(velocidade_kmh)                 as velocidade_media_kmh,
        count(*)                            as n_observacoes
    from {{ ref('fct_viagens') }}
    where velocidade_kmh is not null
    group by 1, 2
),

clima_hora as (
    select
        date_trunc('hour', hora_referencia) as hora_truncada,
        temperatura_c,
        precipitacao_mm,
        velocidade_vento_kmh,
        categoria_chuva
    from {{ ref('stg_weather__horario') }}
)

select
    v.hora_truncada,
    v.codigo_linha,
    v.velocidade_media_kmh,
    v.n_observacoes,
    c.temperatura_c,
    c.precipitacao_mm,
    c.velocidade_vento_kmh,
    c.categoria_chuva
from viagens_hora v
left join clima_hora c using (hora_truncada)
where c.hora_truncada is not null
