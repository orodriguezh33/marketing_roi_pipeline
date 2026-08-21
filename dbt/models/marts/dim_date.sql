-- Grano: un día calendario. Rango derivado de los datos reales (fechas de
-- pedidos + fechas de gasto en ads), no de una fecha fija -- así el spine
-- crece solo a medida que entran más pedidos/gasto en syncs futuros.

with bounds as (

    select
        min(d) as min_date,
        max(d) as max_date
    from (
        select order_purchase_timestamp::date as d
        from {{ ref('stg_postgres__orders') }}
        union all
        select spend_date as d
        from {{ ref('stg_s3__ads_spend') }}
    ) as all_dates

),

spine as (

    select unnest(
        generate_series(bounds.min_date, bounds.max_date, interval '1 day')
    )::date as date_day
    from bounds

)

select
    date_day,
    extract(year from date_day)::int as year,
    extract(month from date_day)::int as month,
    extract(day from date_day)::int as day,
    extract(quarter from date_day)::int as quarter,
    extract(dow from date_day)::int as day_of_week,
    date_trunc('month', date_day)::date as month_date,
    strftime(date_day, '%Y-%m') as month_label
from spine
