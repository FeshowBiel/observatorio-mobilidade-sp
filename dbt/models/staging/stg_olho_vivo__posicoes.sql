{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw', 'olho_vivo_posicoes') }}
),

cleaned as (
    select
        id              as posicao_id,
        coletado_em,
        hora_referencia,
        codigo_linha,
        nullif(prefixo_veiculo, '') as prefixo_veiculo,
        latitude,
        longitude,
        coalesce(acessivel, false) as acessivel
    from source
    where latitude  is not null
      and longitude is not null
      and latitude  between -24.0 and -23.0
      and longitude between -47.0 and -46.0
)

select * from cleaned
