{{ config(materialized='table') }}

select
    codigo_linha,
    letreiro,
    sentido,
    tipo,
    circular,
    denominacao_terminal_principal,
    denominacao_terminal_secundario,
    concat(letreiro, ' - ', denominacao_terminal_principal,
           ' x ', denominacao_terminal_secundario) as nome_completo
from {{ ref('stg_olho_vivo__linhas') }}
