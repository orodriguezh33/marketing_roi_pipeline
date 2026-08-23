# Profiling: `raw_postgres.customers`

Generado: 2026-08-23 14:17 UTC

- **Filas**: 99441
- **Clave candidata**: `customer_id` — sin duplicados

## Columnas

| Columna | Tipo | % nulls | Cardinalidad | Min | Max |
|---|---|---|---|---|---|
| `customer_id` | VARCHAR | 0.0% | 99441 | — | — |
| `customer_city` | VARCHAR | 0.0% | 4119 | — | — |
| `customer_state` | VARCHAR | 0.0% | 27 | — | — |
| `customer_unique_id` | VARCHAR | 0.0% | 96096 | — | — |
| `customer_zip_code_prefix` | BIGINT | 0.0% | 14994 | 1003 | 99990 |
| `_airbyte_extracted_at` | TIMESTAMP | 0.0% | 99441 | 2026-08-21 20:26:25.819000 | 2026-08-21 20:26:41.074388 |

## Frecuencia de valores (columnas de baja cardinalidad)

### `customer_state`

| Valor | Filas |
|---|---|
| `SP` | 41746 |
| `RJ` | 12852 |
| `MG` | 11635 |
| `RS` | 5466 |
| `PR` | 5045 |
| `SC` | 3637 |
| `BA` | 3380 |
| `DF` | 2140 |
| `ES` | 2033 |
| `GO` | 2020 |
| `PE` | 1652 |
| `CE` | 1336 |
| `PA` | 975 |
| `MT` | 907 |
| `MA` | 747 |
| `MS` | 715 |
| `PB` | 536 |
| `PI` | 495 |
| `RN` | 485 |
| `AL` | 413 |
| `SE` | 350 |
| `TO` | 280 |
| `RO` | 253 |
| `AM` | 148 |
| `AC` | 81 |
| `AP` | 68 |
| `RR` | 46 |
