{{ config(materialized='table') }}

select
    p.posicao_id,
    p.coletado_em,
    p.hora_referencia,
    p.codigo_linha,
    p.prefixo_veiculo,
    p.latitude,
    p.longitude,
    p.acessivel,
    d.data_key,
    extract(hour from p.hora_referencia)::int as hora_do_dia,
    d.eh_dia_util,
    d.estacao
from {{ ref('stg_olho_vivo__posicoes') }} p
left join {{ ref('dim_tempo') }} d
    on d.data_key = p.hora_referencia::date
