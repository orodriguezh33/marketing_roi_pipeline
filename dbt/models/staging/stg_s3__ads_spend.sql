-- raw_s3.ads_spend: casting de tipos + normalización de canal vía el seed
-- channel_mapping (ver docs/ROADMAP.md -> Fase 3, decisión #8) -- el join
-- contra un seed de lookup es la misma excepción que en
-- stg_postgres__products, no lógica de negocio.
--
-- Dedup: el generador (generators/generate_ads_spend.py) no sobrescribe
-- CSVs viejos y el sync es "Replicate Source" (full refresh, relee todos los
-- archivos), así que correr el generador dos veces para el mismo día deja
-- dos filas para el mismo (date, channel) con montos distintos. Mismo
-- criterio que stg_postgres__order_reviews: nos quedamos con la más
-- reciente por _airbyte_extracted_at.

with source as (

    select *
    from {{ source('raw_s3', 'ads_spend') }}

),

normalized as (

    select
        source.date::date as spend_date,
        coalesce(mapping.canonical_channel, source.channel) as channel,
        source.spend::double as spend,
        source.currency,
        source._airbyte_extracted_at
    from source
    left join {{ ref('channel_mapping') }} as mapping
        on source.channel = mapping.raw_channel

),

deduped as (

    select
        *,
        row_number() over (
            partition by spend_date, channel
            order by _airbyte_extracted_at desc
        ) as rn
    from normalized

)

select
    spend_date,
    channel,
    spend,
    currency,
    _airbyte_extracted_at
from deduped
where rn = 1
