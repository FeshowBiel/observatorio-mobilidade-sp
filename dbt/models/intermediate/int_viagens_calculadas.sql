{{ config(materialized='view') }}

with posicoes as (
    select * from {{ ref('stg_olho_vivo__posicoes') }}
),

com_lag as (
    select
        posicao_id,
        prefixo_veiculo,
        codigo_linha,
        hora_referencia,
        latitude,
        longitude,
        lag(latitude)       over w as lat_anterior,
        lag(longitude)      over w as lon_anterior,
        lag(hora_referencia) over w as hora_anterior
    from posicoes
    where prefixo_veiculo is not null
    window w as (
        partition by prefixo_veiculo
        order by hora_referencia
    )
),

calculado as (
    select
        *,
        extract(epoch from (hora_referencia - hora_anterior)) / 60.0 as minutos_diff,
        -- Haversine simplificado
        2 * 6371 * asin(sqrt(
            power(sin(radians(latitude  - lat_anterior)  / 2), 2) +
            cos(radians(lat_anterior)) * cos(radians(latitude)) *
            power(sin(radians(longitude - lon_anterior) / 2), 2)
        )) as km_diff
    from com_lag
    where hora_anterior is not null
)

select
    *,
    case
        when minutos_diff > 0 then (km_diff / minutos_diff) * 60
        else null
    end as velocidade_kmh
from calculado
where minutos_diff between 0.1 and 30
