{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw', 'olho_vivo_linhas') }}
),

deduped as (
    select distinct on (codigo_linha, sentido)
        id              as linha_id,
        coletado_em,
        codigo_linha,
        circular,
        letreiro,
        sentido,
        tipo,
        denominacao_terminal_principal,
        denominacao_terminal_secundario
    from source
    order by codigo_linha, sentido, coletado_em desc
)

select * from deduped
