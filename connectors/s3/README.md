# S3 (MinIO) — `minio-ads-spend`

Gasto de ads por canal/fecha (`generators/generate_ads_spend.py`) y, desde Fase 3 —
Ampliación (decisión #15, ver `docs/ROADMAP.md`), atribución de marketing a nivel de
orden (`generators/generate_attribution.py`): ambos generadores escriben CSVs al mismo
bucket MinIO local (sustituto de S3), en prefijos distintos.

## Source

- Tipo: **S3** (endpoint override para compatibilidad con MinIO). Conector deployado:
  `source-s3:4.15.18` (file-based CDK, "v4") — los campos "Output Stream Name" /
  "Pattern of files to replicate" / "File Format" a nivel raíz están **deprecados**,
  no usarlos: el stream se define dentro de la lista "Streams".
- Endpoint: `http://host.docker.internal:${MINIO_PORT}`.
- Bucket: `ads-spend`.
- Access key / secret: `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD`.
- Streams → dos streams (misma Source, no una connection nueva):
  - Name: `ads_spend`.
    - Globs: `raw/ads_spend/*.csv` (lista — agregar el patrón como entrada).
    - Format: CSV.
  - Name: `attribution` (agregado en la Ampliación 2026-08-24).
    - Globs: `raw/attribution/*.csv`.
    - Format: CSV.
- Delivery Method: **Replicate Records** (default).
- Sync mode, ambos streams: **Full refresh | Replicate Source** (no "Append Historical
  Changes") — ninguno de los dos generadores sobrescribe CSVs viejos, cada sync relee
  todos los archivos que matchean el glob, así que "Append Historical Changes"
  duplicaría filas de archivos ya sincronizados en corridas anteriores.

## Destination

- `motherduck-raw-s3` → `md:marketing_roi`, `schema = raw_s3` (**guión bajo, no
  guión medio** — ver Troubleshooting).

## Troubleshooting

**`No streams are available for source SourceS3`** — la lista "Streams" quedó vacía
(fácil de pasar por alto si se sigue la terminología vieja de "Path Pattern" como
campo suelto). Hay que agregar explícitamente una entrada en "The list of streams to
sync" con Name/Globs/Format como arriba.

**`primary key missing`** — pasa si el stream queda en un modo con dedup (p. ej.
"Full Refresh | Append + Deduped"). El CSV de ads spend no tiene ninguna columna que
sirva de identificador único — usar "Replicate Source", que no requiere primary key.

**`ValueError: Invalid SQL name: raw-s3`** — no es un error de la Source, es de la
Destination: el conector MotherDuck valida el `schema` como identificador SQL
(`validated_sql_name` en `destination.py`) y un guión medio lo rechaza. El
stacktrace que se ve en el job muestra `Broken pipe`/`Channel was closed`, que es
solo el orchestrator notando que el proceso de destino murió — no la causa raíz. Usar
`raw_s3`, no `raw-s3`, en el campo `schema` de la Destination.

## Estado

Verificado en MotherDuck: `raw_s3.ads_spend` con 4388 filas. `raw_s3.attribution`
(stream nuevo, Ampliación 2026-08-24): generadores corridos y CSVs subidos a MinIO —
falta agregar el stream en la UI de Airbyte y correr el sync para que aparezca en
MotherDuck.
