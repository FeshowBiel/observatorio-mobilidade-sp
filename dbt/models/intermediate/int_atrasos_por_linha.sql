{{ config(materialized='view') }}

with viagens as (
    select * from {{ ref('int_viagens_calculadas') }}
),

por_linha_hora as (
    select
        codigo_linha,
        date_trunc('hour', hora_referencia) as hora_truncada,
        count(*)                            as n_observacoes,
        avg(velocidade_kmh)                 as velocidade_media_kmh,
        stddev(velocidade_kmh)              as velocidade_stddev_kmh,
        percentile_cont(0.5) within group (
            order by velocidade_kmh
        )                                   as velocidade_mediana_kmh,
        avg(minutos_diff)                   as intervalo_medio_min
    from viagens
    where velocidade_kmh is not null
      and velocidade_kmh between 1 and 120
    group by 1, 2
)

select * from por_linha_hora
