-- 1:1 con raw_postgres.sellers. seller_id es PK en Postgres, sin dedup
-- necesario. Filtra tombstones de CDC (_ab_cdc_deleted_at).

with source as (

    select *
    from {{ source('raw_postgres', 'sellers') }}
    where _ab_cdc_deleted_at is null

)

select
    seller_id,
    seller_city,
    seller_state,
    seller_zip_code_prefix,
    _airbyte_extracted_at
from source
