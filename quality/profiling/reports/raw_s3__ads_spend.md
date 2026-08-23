# Profiling: `raw_s3.ads_spend`

Generado: 2026-08-23 14:17 UTC

- **Filas**: 4388
- **Clave candidata**: `date`, `channel` — sin duplicados

## Columnas

| Columna | Tipo | % nulls | Cardinalidad | Min | Max |
|---|---|---|---|---|---|
| `date` | VARCHAR | 0.0% | 1097 | — | — |
| `spend` | VARCHAR | 0.0% | 4352 | — | — |
| `channel` | VARCHAR | 0.0% | 8 | — | — |
| `currency` | VARCHAR | 0.0% | 1 | — | — |
| `_ab_source_file_url` | VARCHAR | 100.0% | 0 | — | — |
| `_ab_source_file_last_modified` | VARCHAR | 100.0% | 0 | — | — |
| `_airbyte_extracted_at` | TIMESTAMP | 0.0% | 4388 | 2026-08-22 17:27:03.398420 | 2026-08-22 17:27:14.604348 |

## Frecuencia de valores (columnas de baja cardinalidad)

### `channel`

| Valor | Filas |
|---|---|
| `facebook_ads` | 1096 |
| `email_marketing` | 1096 |
| `instagram_ads` | 1096 |
| `google_ads` | 1096 |
| `FacebookAds` | 1 |
| `GoogleAds` | 1 |
| `InstagramAds` | 1 |
| `EmailMarketing` | 1 |

### `currency`

| Valor | Filas |
|---|---|
| `BRL` | 4388 |

### `_ab_source_file_url`

| Valor | Filas |
|---|---|
| `None` | 4388 |

### `_ab_source_file_last_modified`

| Valor | Filas |
|---|---|
| `None` | 4388 |
