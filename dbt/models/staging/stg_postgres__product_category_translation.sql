-- 1:1 con raw_postgres.product_category_name_translation. Tabla de lookup
-- estática (CSV de Olist) -- pass-through, la usa stg_postgres__products
-- para traducir la categoría a inglés.

with source as (

    select *
    from {{ source('raw_postgres', 'product_category_name_translation') }}
    where _ab_cdc_deleted_at is null

)

select
    product_category_name,
    product_category_name_english
from source
