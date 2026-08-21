-- Grano: canal x fecha. Ningún pedido/pago tiene un campo de canal de
-- marketing (ni en Postgres ni en Stripe) -- no existe attribution real a
-- nivel de orden en los datos de origen. Por decisión explícita del negocio
-- (no inventada acá), el revenue y los clientes nuevos del día se reparten
-- entre los canales activos ese día en proporción a su share de spend
-- (`spend_share`). Es una estimación de atribución, no un hecho medido --
-- se deja `spend_share` visible en el mart para que el consumidor sepa que
-- `attributed_revenue`/`attributed_new_customers` son derivados, no reales.

with orders_customers as (

    select
        fct_orders.order_id,
        fct_orders.order_purchase_timestamp::date as order_date,
        fct_orders.payment_value,
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

daily_company as (

    select
        orders_customers.order_date,
        sum(orders_customers.payment_value) as daily_revenue,
        count(distinct case
            when orders_customers.order_date = first_orders.first_order_date
            then orders_customers.customer_unique_id
        end) as daily_new_customers
    from orders_customers
    left join first_orders
        on orders_customers.customer_unique_id = first_orders.customer_unique_id
    group by orders_customers.order_date

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
    coalesce(daily_company.daily_revenue, 0) * daily_channel_spend.spend_share
        as attributed_revenue,
    coalesce(daily_company.daily_new_customers, 0) * daily_channel_spend.spend_share
        as attributed_new_customers,
    budget.budget_target,
    case
        when coalesce(daily_company.daily_new_customers, 0) * daily_channel_spend.spend_share > 0
        then daily_channel_spend.spend
            / (coalesce(daily_company.daily_new_customers, 0) * daily_channel_spend.spend_share)
    end as cac,
    case
        when daily_channel_spend.spend > 0
        then (coalesce(daily_company.daily_revenue, 0) * daily_channel_spend.spend_share)
            / daily_channel_spend.spend
    end as roas
from daily_channel_spend
left join daily_company
    on daily_channel_spend.spend_date = daily_company.order_date
left join budget
    on daily_channel_spend.channel = budget.channel
    and strftime(daily_channel_spend.spend_date, '%Y-%m') = budget.month
