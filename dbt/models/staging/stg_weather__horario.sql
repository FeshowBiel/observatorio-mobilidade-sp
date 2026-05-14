{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw', 'weather_horario') }}
),

cleaned as (
    select
        id              as weather_id,
        hora_referencia,
        coletado_em,
        latitude,
        longitude,
        temperatura_c,
        coalesce(precipitacao_mm, 0)      as precipitacao_mm,
        coalesce(velocidade_vento_kmh, 0) as velocidade_vento_kmh,
        case
            when coalesce(precipitacao_mm, 0) = 0     then 'sem_chuva'
            when precipitacao_mm < 2.5                then 'chuva_fraca'
            when precipitacao_mm < 10                 then 'chuva_moderada'
            else                                           'chuva_forte'
        end as categoria_chuva
    from source
)

select * from cleaned
