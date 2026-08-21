-- Grano: un canal canónico. Fuente = los 4 valores distintos del seed
-- channel_mapping (ver docs/ROADMAP.md -> Fase 3, decisión #8), no un
-- literal hardcodeado acá.

select distinct
    canonical_channel as channel
from {{ ref('channel_mapping') }}
