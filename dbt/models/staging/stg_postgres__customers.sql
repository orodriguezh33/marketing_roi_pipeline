-- 1:1 con raw_postgres.customers. customer_id es PK en Postgres, sin dedup
-- necesario. Filtra tombstones de CDC (_ab_cdc_deleted_at).

with source as (

    select *
    from {{ source('raw_postgres', 'customers') }}
    where _ab_cdc_deleted_at is null

)

select
    customer_id,
    customer_unique_id,
    customer_city,
    customer_state,
    customer_zip_code_prefix,
    _airbyte_extracted_at
from source
