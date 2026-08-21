-- 1:1 con raw_stripe.charges. `id` es único por diseño de Stripe, sin dedup
-- necesario. `order_id` sale de metadata.order_id (generators/generate_stripe.py
-- lo setea al crear el charge) -- es el vínculo hacia raw_postgres.orders.
--
-- amount viene en centavos (convención de Stripe) -- se convierte a unidades
-- de moneda acá para que payment_value (order_payments, ya en BRL) y esta
-- columna sean directamente comparables/sumables en fct_orders.
--
-- payment_source = 'stripe' identifica el sistema de origen, igual que
-- stg_postgres__order_payments (payment_source = 'legacy').

with source as (

    select *
    from {{ source('raw_stripe', 'charges') }}

)

select
    id as charge_id,
    metadata ->> 'order_id' as order_id,
    customer as stripe_customer_id,
    amount / 100.0 as amount,
    upper(currency) as currency,
    status,
    paid,
    captured,
    refunded,
    to_timestamp(created)::timestamp as created_at,
    'stripe' as payment_source,
    _airbyte_extracted_at
from source
