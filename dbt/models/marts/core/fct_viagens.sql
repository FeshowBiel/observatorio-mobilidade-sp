{{ config(materialized='table') }}

select
    v.posicao_id,
    v.prefixo_veiculo,
    v.codigo_linha,
    l.letreiro,
    l.denominacao_terminal_principal,
    v.hora_referencia,
    v.hora_anterior,
    v.minutos_diff,
    v.km_diff,
    v.velocidade_kmh,
    d.data_key,
    d.eh_dia_util,
    d.estacao,
    extract(hour from v.hora_referencia)::int as hora_do_dia,
    case
        when extract(hour from v.hora_referencia) between 6  and 9  then 'pico_manha'
        when extract(hour from v.hora_referencia) between 17 and 20 then 'pico_tarde'
        when extract(hour from v.hora_referencia) between 22 and 23 then 'noturno'
        when extract(hour from v.hora_referencia) between 0  and 5  then 'madrugada'
        else 'fora_pico'
    end as periodo_dia
from {{ ref('int_viagens_calculadas') }} v
left join {{ ref('dim_linha') }} l using (codigo_linha)
left join {{ ref('dim_tempo') }} d
    on d.data_key = v.hora_referencia::date
