-- raw_s3.attribution: casting de tipos + normalización de canal vía el seed
-- channel_mapping, mismo patrón que stg_s3__ads_spend (ver docs/ROADMAP.md ->
-- Fase 3, Ampliación, decisión #15).
--
-- Grano: un order_id (no todo order_id aparece acá -- generators/
-- generate_attribution.py deja sin fila una fracción de pedidos a propósito,
-- para simular revenue direct/organic sin touchpoint de marketing).
--
-- Dedup: mismo criterio que stg_s3__ads_spend -- el generador no sobrescribe
-- CSVs viejos y el sync es "Replicate Source" (full refresh, relee todos los
-- archivos), así que corridas repetidas para el mismo rango de fechas pueden
-- dejar más de una fila para el mismo order_id. Nos quedamos con la más
-- reciente por _airbyte_extracted_at.

with source as (

    select *
    from {{ source('raw_s3', 'attribution') }}

),

normalized as (

    select
        source.order_id,
        coalesce(mapping.canonical_channel, source.channel) as channel,
        source.attributed_at::timestamp as attributed_at,
        source.touchpoint,
        source._airbyte_extracted_at
    from source
    left join {{ ref('channel_mapping') }} as mapping
        on source.channel = mapping.raw_channel

),

deduped as (

    select
        *,
        row_number() over (
            partition by order_id
            order by _airbyte_extracted_at desc
        ) as rn
    from normalized

)

select
    order_id,
    channel,
    attributed_at,
    touchpoint,
    _airbyte_extracted_at
from deduped
where rn = 1
