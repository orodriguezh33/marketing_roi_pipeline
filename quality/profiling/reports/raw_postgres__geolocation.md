# Profiling: `raw_postgres.geolocation`

Generado: 2026-08-23 14:17 UTC

- **Filas**: 1000163
- **Clave candidata**: ninguna configurada (ver `CANDIDATE_KEYS` en `run_profiling.py`)

## Columnas

| Columna | Tipo | % nulls | Cardinalidad | Min | Max |
|---|---|---|---|---|---|
| `geolocation_lat` | DECIMAL(38,9) | 0.0% | 717188 | -36.605374411 | 45.065933183 |
| `geolocation_lng` | DECIMAL(38,9) | 0.0% | 717480 | -101.466766449 | 121.105393811 |
| `geolocation_city` | VARCHAR | 0.0% | 8011 | — | — |
| `geolocation_state` | VARCHAR | 0.0% | 27 | — | — |
| `geolocation_zip_code_prefix` | BIGINT | 0.0% | 19015 | 1001 | 99990 |
| `_airbyte_extracted_at` | TIMESTAMP | 0.0% | 1000162 | 2026-08-22 17:20:05.782733 | 2026-08-22 17:22:56.791812 |

## Frecuencia de valores (columnas de baja cardinalidad)

### `geolocation_state`

| Valor | Filas |
|---|---|
| `SP` | 404268 |
| `MG` | 126336 |
| `RJ` | 121169 |
| `RS` | 61851 |
| `PR` | 57859 |
| `SC` | 38328 |
| `BA` | 36045 |
| `GO` | 20139 |
| `ES` | 16748 |
| `PE` | 16432 |
| `DF` | 12986 |
| `MT` | 12031 |
| `CE` | 11674 |
| `PA` | 10853 |
| `MS` | 10431 |
| `MA` | 7853 |
| `PB` | 5538 |
| `RN` | 5041 |
| `PI` | 4549 |
| `AL` | 4183 |
| `TO` | 3576 |
| `SE` | 3563 |
| `RO` | 3478 |
| `AM` | 2432 |
| `AC` | 1301 |
| `AP` | 853 |
| `RR` | 646 |
