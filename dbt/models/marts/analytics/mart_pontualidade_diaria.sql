{{ config(materialized='table') }}

select
    v.data_key                          as data,
    v.codigo_linha,
    l.letreiro,
    l.denominacao_terminal_principal,
    l.denominacao_terminal_secundario,
    count(*)                            as viagens_total,
    count(distinct v.prefixo_veiculo)   as veiculos_unicos,
    round(avg(v.velocidade_kmh)::numeric, 2)    as velocidade_media_kmh,
    round(stddev(v.velocidade_kmh)::numeric, 2) as velocidade_stddev_kmh,
    round(avg(v.minutos_diff)::numeric, 2)      as intervalo_medio_min,
    -- Pontualidade: % de segmentos com velocidade dentro de ±1 desvio padrão da média da linha
    round(
        100.0 * sum(
            case when abs(v.velocidade_kmh - avg(v.velocidade_kmh) over (
                    partition by v.codigo_linha, v.data_key)
                ) <= stddev(v.velocidade_kmh) over (
                    partition by v.codigo_linha, v.data_key)
            then 1 else 0 end
        )::numeric / nullif(count(*), 0)
    , 2) as pontualidade_pct,
    v.eh_dia_util,
    v.estacao
from {{ ref('fct_viagens') }} v
left join {{ ref('dim_linha') }} l using (codigo_linha)
where v.data_key is not null
group by 1, 2, 3, 4, 5, v.eh_dia_util, v.estacao
