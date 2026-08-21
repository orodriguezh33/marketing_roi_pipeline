-- 1:1 con raw_postgres.orders. order_id es PK en Postgres, sin dedup
-- necesario. Filtra tombstones de CDC (_ab_cdc_deleted_at).
--
-- Regla de nulls (decisión #11, ver docs/ROADMAP.md -> Fase 3): los
-- timestamps de entrega se dejan nulos tal cual -- un null significa "esa
-- etapa todavía no ocurrió", no "dato faltante". is_delivered resume esa
-- lógica para no obligar a cada consumidor a repetirla.

with source as (

    select *
    from {{ source('raw_postgres', 'orders') }}
    where _ab_cdc_deleted_at is null

)

select
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date,
    order_delivered_customer_date is not null as is_delivered,
    _airbyte_extracted_at
from source
