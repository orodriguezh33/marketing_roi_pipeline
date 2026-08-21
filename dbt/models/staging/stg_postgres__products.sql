-- 1:1 con raw_postgres.products, más la traducción de categoría a inglés.
-- Excepción deliberada a "sin joins en staging": es un join de limpieza
-- contra una tabla de lookup estática, no lógica de negocio (ver
-- docs/ROADMAP.md -> Fase 3, "Traducir product_category_name...").

with source as (

    select *
    from {{ source('raw_postgres', 'products') }}
    where _ab_cdc_deleted_at is null

),

translation as (

    select * from {{ ref('stg_postgres__product_category_translation') }}

)

select
    source.product_id,
    source.product_category_name,
    translation.product_category_name_english,
    source.product_name_lenght as product_name_length,
    source.product_description_lenght as product_description_length,
    source.product_photos_qty,
    source.product_weight_g,
    source.product_length_cm,
    source.product_height_cm,
    source.product_width_cm,
    source._airbyte_extracted_at
from source
left join translation
    on source.product_category_name = translation.product_category_name
