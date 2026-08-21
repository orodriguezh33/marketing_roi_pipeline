-- 1:1 con raw_postgres.order_items. PK compuesta (order_id, order_item_id)
-- en Postgres, sin dedup necesario. Filtra tombstones de CDC.

with source as (

    select *
    from {{ source('raw_postgres', 'order_items') }}
    where _ab_cdc_deleted_at is null

)

select
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date,
    price,
    freight_value,
    _airbyte_extracted_at
from source
