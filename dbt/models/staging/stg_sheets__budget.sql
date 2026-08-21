-- raw_sheets.budget: 1:1 con la hoja, solo casting (todas las columnas de
-- negocio llegan como VARCHAR desde el connector de Sheets). `channel` ya
-- viene en forma canónica en esta fuente (es mantenida por el negocio, ver
-- generators/generate_budget.py -> CHANNELS), así que no necesita pasar por
-- channel_mapping.
--
-- budget_target llega con coma decimal (ej. "30102,65") -- el locale del
-- Sheet lo formatea así aunque el generador escribe un float con punto; se
-- normaliza antes de castear.

with source as (

    select *
    from {{ source('raw_sheets', 'budget') }}

)

select
    month,
    channel,
    replace(budget_target, ',', '.')::double as budget_target,
    _airbyte_extracted_at
from source
