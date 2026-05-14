{{ config(materialized='table') }}

with base as (
    select
        data_key,
        codigo_linha,
        eh_dia_util,
        estacao,
        velocidade_kmh,
        minutos_diff,
        prefixo_veiculo
    from {{ ref('fct_viagens') }}
    where data_key is not null
),

stats_por_linha_dia as (
    select
        data_key,
        codigo_linha,
        avg(velocidade_kmh)    as media_kmh,
        stddev(velocidade_kmh) as stddev_kmh
    from base
    group by 1, 2
),

com_stats as (
    select
        b.*,
        s.media_kmh,
        s.stddev_kmh,
        case
            when s.stddev_kmh is not null and s.stddev_kmh > 0
             and abs(b.velocidade_kmh - s.media_kmh) <= s.stddev_kmh
            then 1 else 0
        end as dentro_desvio
    from base b
    join stats_por_linha_dia s using (data_key, codigo_linha)
)

select
    v.data_key                                          as data,
    v.codigo_linha,
    l.letreiro,
    l.denominacao_terminal_principal,
    l.denominacao_terminal_secundario,
    count(*)                                            as viagens_total,
    count(distinct v.prefixo_veiculo)                  as veiculos_unicos,
    round(avg(v.velocidade_kmh)::numeric, 2)           as velocidade_media_kmh,
    round(stddev(v.velocidade_kmh)::numeric, 2)        as velocidade_stddev_kmh,
    round(avg(v.minutos_diff)::numeric, 2)             as intervalo_medio_min,
    round(100.0 * sum(v.dentro_desvio) / nullif(count(*), 0), 2) as pontualidade_pct,
    v.eh_dia_util,
    v.estacao
from com_stats v
left join {{ ref('dim_linha') }} l using (codigo_linha)
group by 1, 2, 3, 4, 5, v.eh_dia_util, v.estacao
