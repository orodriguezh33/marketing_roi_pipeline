# Profiling: `raw_postgres.sellers`

Generado: 2026-08-23 14:17 UTC

- **Filas**: 3095
- **Clave candidata**: `seller_id` — sin duplicados

## Columnas

| Columna | Tipo | % nulls | Cardinalidad | Min | Max |
|---|---|---|---|---|---|
| `seller_id` | VARCHAR | 0.0% | 3095 | — | — |
| `seller_city` | VARCHAR | 0.0% | 611 | — | — |
| `seller_state` | VARCHAR | 0.0% | 23 | — | — |
| `seller_zip_code_prefix` | BIGINT | 0.0% | 2246 | 1001 | 99730 |
| `_airbyte_extracted_at` | TIMESTAMP | 0.0% | 3095 | 2026-08-21 20:27:27.240169 | 2026-08-21 20:27:27.775996 |

## Frecuencia de valores (columnas de baja cardinalidad)

### `seller_state`

| Valor | Filas |
|---|---|
| `SP` | 1849 |
| `PR` | 349 |
| `MG` | 244 |
| `SC` | 190 |
| `RJ` | 171 |
| `RS` | 129 |
| `GO` | 40 |
| `DF` | 30 |
| `ES` | 23 |
| `BA` | 19 |
| `CE` | 13 |
| `PE` | 9 |
| `PB` | 6 |
| `MS` | 5 |
| `RN` | 5 |
| `MT` | 4 |
| `SE` | 2 |
| `RO` | 2 |
| `AC` | 1 |
| `PI` | 1 |
| `PA` | 1 |
| `AM` | 1 |
| `MA` | 1 |
