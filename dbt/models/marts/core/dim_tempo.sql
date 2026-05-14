{{ config(materialized='table') }}

with dates as (
    select generate_series(
        '2025-01-01'::date,
        '2026-12-31'::date,
        '1 day'::interval
    )::date as data
)

select
    data                                                    as data_key,
    extract(year  from data)::int                          as ano,
    extract(month from data)::int                          as mes,
    extract(day   from data)::int                          as dia,
    extract(dow   from data)::int                          as dia_semana_num,
    extract(week  from data)::int                          as semana_ano,
    to_char(data, 'TMDay')                                 as nome_dia,
    to_char(data, 'TMMonth')                               as nome_mes,
    case when extract(dow from data) in (0, 6) then false
         else true end                                     as eh_dia_util,
    case
        when extract(month from data) in (12, 1, 2) then 'Verão'
        when extract(month from data) in (3, 4, 5)  then 'Outono'
        when extract(month from data) in (6, 7, 8)  then 'Inverno'
        else 'Primavera'
    end                                                    as estacao
from dates
