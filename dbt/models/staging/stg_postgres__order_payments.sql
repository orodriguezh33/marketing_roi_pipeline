-- 1:1 con raw_postgres.order_payments. PK compuesta (order_id,
-- payment_sequential) en Postgres, sin dedup necesario. Filtra tombstones
-- de CDC.
--
-- payment_source = 'legacy' identifica el sistema de origen -- fct_orders
-- (Fase 3, marts) unifica esto con stg_stripe__charges (payment_source =
-- 'stripe') en un solo concepto de pago, ver docs/ROADMAP.md -> Fase 3.

with source as (

    select *
    from {{ source('raw_postgres', 'order_payments') }}
    where _ab_cdc_deleted_at is null

)

select
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value,
    'legacy' as payment_source,
    _airbyte_extracted_at
from source
