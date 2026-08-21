-- raw_postgres.order_reviews no tiene PK -- el dataset real trae ~100 filas
-- con review_id duplicado (documentado en infra/postgres/init/01_schema.sql).
-- Sin _ab_cdc_deleted_at (esta tabla no tiene PK en Postgres, Airbyte no le
-- genera columnas de dedup de CDC), así que el dedup se hace acá.
--
-- Regla (decisión #10, ver docs/ROADMAP.md -> Fase 3): por cada review_id
-- duplicado, nos quedamos con la fila de review_answer_timestamp más
-- reciente.

with source as (

    select *
    from {{ source('raw_postgres', 'order_reviews') }}

),

deduped as (

    select
        *,
        row_number() over (
            partition by review_id
            order by review_answer_timestamp desc
        ) as rn
    from source

)

select
    review_id,
    order_id,
    review_score,
    review_comment_title,
    review_comment_message,
    review_creation_date,
    review_answer_timestamp,
    _airbyte_extracted_at
from deduped
where rn = 1
