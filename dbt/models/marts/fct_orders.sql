-- Grano: un order_id. Reconcilia dos sistemas de pago (decisión de diseño,
-- ver docs/ROADMAP.md -> narrativa de datos): pagos legacy en Postgres
-- (order_payments, puede tener varias filas por pedido por cuotas) y
-- charges post-migración en Stripe (1 charge por pedido).
--
-- Stripe tiene prioridad sobre legacy cuando ambos existen para el mismo
-- order_id -- NO se suman. generators/generate_stripe.py crea el charge de
-- Stripe usando el mismo payment_value que ya está en order_payments (toma
-- pedidos recientes insertados por generate_orders.py, que ya escribe su
-- propia fila legacy) -- son el mismo cobro representado en el sistema
-- nuevo, no un segundo pago independiente. Sumar ambos duplicaría revenue
-- para esos pedidos.
--
-- marketing_channel viene de stg_s3__attribution (export tipo GA4/UTM
-- last-click, ver docs/ROADMAP.md -> Fase 3, Ampliación, decisión #15).
-- NULL es un valor legítimo -- direct/organic, sin touchpoint de marketing --
-- no un dato faltante.

with items as (

    select
        order_id,
        count(*) as item_count,
        sum(price) as items_price,
        sum(freight_value) as freight_value
    from {{ ref('stg_postgres__order_items') }}
    group by order_id

),

payments_legacy as (

    select
        order_id,
        sum(payment_value) as amount
    from {{ ref('stg_postgres__order_payments') }}
    group by order_id

),

payments_stripe as (

    select
        order_id,
        sum(amount) as amount
    from {{ ref('stg_stripe__charges') }}
    where order_id is not null
    group by order_id

),

payments as (

    select
        coalesce(payments_legacy.order_id, payments_stripe.order_id) as order_id,
        coalesce(payments_stripe.amount, payments_legacy.amount) as payment_value,
        case
            when payments_stripe.amount is not null then 'stripe'
            else 'legacy'
        end as payment_source
    from payments_legacy
    full outer join payments_stripe
        on payments_legacy.order_id = payments_stripe.order_id

),

orders as (

    select * from {{ ref('stg_postgres__orders') }}

),

attribution as (

    select * from {{ ref('stg_s3__attribution') }}

)

select
    orders.order_id,
    orders.customer_id,
    orders.order_status,
    orders.order_purchase_timestamp,
    orders.order_approved_at,
    orders.order_delivered_carrier_date,
    orders.order_delivered_customer_date,
    orders.order_estimated_delivery_date,
    orders.is_delivered,
    items.item_count,
    items.items_price,
    items.freight_value,
    coalesce(items.items_price, 0) + coalesce(items.freight_value, 0) as order_value,
    payments.payment_value,
    payments.payment_source,
    attribution.channel as marketing_channel
from orders
left join items on orders.order_id = items.order_id
left join payments on orders.order_id = payments.order_id
left join attribution on orders.order_id = attribution.order_id
