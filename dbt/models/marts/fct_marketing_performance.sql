-- Grano: canal x fecha. Hasta la Fase 3 original, ningún pedido/pago traía
-- canal de marketing y este mart repartía revenue/clientes nuevos del día
-- proporcional al spend_share -- eso colapsaba ROAS/CAC a un único valor
-- idéntico para los 4 canales cada día (spend_canal se cancela
-- algebraicamente al dividir attributed_revenue = daily_revenue *
-- spend_share entre spend_canal). Documentado como limitación conocida en
-- docs/ROADMAP.md Fase 3 decisión #14 y en la nota de Fase 4 sobre el
-- `mostly=0.98` de la expectation de cac.
--
-- Fase 3 -- Ampliación (decisión #15, ver docs/ROADMAP.md) reemplaza esa
-- estimación por atribución medida: fct_orders.marketing_channel viene de
-- un feed de atribución (stg_s3__attribution, simula un export tipo
-- GA4/UTM last-click) que ahora asigna canal a nivel de orden.
-- attributed_revenue/attributed_new_customers/cac/roas son sumas/conteos
-- reales de pedidos por (fecha, canal), ya no un reparto proporcional.
--
-- Una fracción de pedidos queda sin marketing_channel (direct/organic, sin
-- touchpoint) -- ese revenue no entra en ningún canal de este mart a
-- propósito (ver analyst_portfolio para el % reportado). spend_share se
-- conserva como columna informativa (share de presupuesto por canal), ya
-- no participa en el cálculo de attributed_revenue/attributed_new_customers.
--
-- `budget_target` es NULL para todo el histórico Olist (2016-2018): decisión
-- de negocio explícita, no bug -- generate_budget.py solo escribe metas para
-- el año en curso (operación actual), no un backfill retroactivo para años
-- previos al proyecto. El histórico sirve para revenue/spend/ROAS, no para
-- budget-vs-actual.
--
-- Hueco 2019-2025: decisión de negocio explícita, no bug de sync. Olist real
-- termina en oct-2018; generate_orders.py/generate_ads_spend.py simulan
-- actividad "actual" (hoy), no un backfill retroactivo de esos 7 años. El
-- mart salta de oct-2018 a la fecha real de operación (2026 en adelante) --
-- un consumidor (ej. Power BI) debe anotar o filtrar el gap, no interpretarlo
-- como datos faltantes de un sync roto.

with orders_customers as (

    select
        fct_orders.order_id,
        fct_orders.order_purchase_timestamp::date as order_date,
        fct_orders.payment_value,
        fct_orders.marketing_channel,
        dim_customer.customer_unique_id
    from {{ ref('fct_orders') }} as fct_orders
    left join {{ ref('dim_customer') }} as dim_customer
        on fct_orders.customer_id = dim_customer.customer_id

),

first_orders as (

    select
        customer_unique_id,
        min(order_date) as first_order_date
    from orders_customers
    group by customer_unique_id

),

daily_channel_performance as (

    select
        orders_customers.order_date,
        orders_customers.marketing_channel as channel,
        sum(orders_customers.payment_value) as attributed_revenue,
        count(distinct case
            when orders_customers.order_date = first_orders.first_order_date
            then orders_customers.customer_unique_id
        end) as attributed_new_customers
    from orders_customers
    left join first_orders
        on orders_customers.customer_unique_id = first_orders.customer_unique_id
    -- marketing_channel NULL = direct/organic, sin touchpoint -- ese revenue
    -- no se atribuye a ningún canal (ver header).
    where orders_customers.marketing_channel is not null
    group by orders_customers.order_date, orders_customers.marketing_channel

),

daily_channel_spend as (

    select
        spend_date,
        channel,
        spend,
        case
            when sum(spend) over (partition by spend_date) > 0
            then spend / sum(spend) over (partition by spend_date)
            else 0
        end as spend_share
    from {{ ref('stg_s3__ads_spend') }}

),

budget as (

    select
        month,
        channel,
        budget_target
    from {{ ref('stg_sheets__budget') }}

)

select
    daily_channel_spend.spend_date as date_day,
    daily_channel_spend.channel,
    daily_channel_spend.spend,
    daily_channel_spend.spend_share,
    coalesce(daily_channel_performance.attributed_revenue, 0) as attributed_revenue,
    coalesce(daily_channel_performance.attributed_new_customers, 0)
        as attributed_new_customers,
    budget.budget_target,
    case
        when coalesce(daily_channel_performance.attributed_new_customers, 0) > 0
        then daily_channel_spend.spend / daily_channel_performance.attributed_new_customers
    end as cac,
    case
        when daily_channel_spend.spend > 0
        then coalesce(daily_channel_performance.attributed_revenue, 0)
            / daily_channel_spend.spend
    end as roas
from daily_channel_spend
left join daily_channel_performance
    on daily_channel_spend.spend_date = daily_channel_performance.order_date
    and daily_channel_spend.channel = daily_channel_performance.channel
left join budget
    on daily_channel_spend.channel = budget.channel
    and strftime(daily_channel_spend.spend_date, '%Y-%m') = budget.month
