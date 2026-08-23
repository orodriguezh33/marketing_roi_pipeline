# Profiling: `raw_postgres.products`

Generado: 2026-08-23 14:17 UTC

- **Filas**: 32951
- **Clave candidata**: `product_id` — sin duplicados

## Columnas

| Columna | Tipo | % nulls | Cardinalidad | Min | Max |
|---|---|---|---|---|---|
| `product_id` | VARCHAR | 0.0% | 32951 | — | — |
| `product_weight_g` | BIGINT | 0.01% | 2204 | 0 | 40425 |
| `product_width_cm` | BIGINT | 0.01% | 95 | 6 | 118 |
| `product_height_cm` | BIGINT | 0.01% | 102 | 2 | 105 |
| `product_length_cm` | BIGINT | 0.01% | 99 | 7 | 105 |
| `product_photos_qty` | BIGINT | 1.85% | 19 | 1 | 20 |
| `product_name_lenght` | BIGINT | 1.85% | 66 | 5 | 76 |
| `product_category_name` | VARCHAR | 1.85% | 73 | — | — |
| `product_description_lenght` | BIGINT | 1.85% | 2960 | 4 | 3992 |
| `_airbyte_extracted_at` | TIMESTAMP | 0.0% | 32951 | 2026-08-21 20:27:27.776533 | 2026-08-21 20:27:34.383711 |

## Frecuencia de valores (columnas de baja cardinalidad)

### `product_photos_qty`

| Valor | Filas |
|---|---|
| `1` | 16489 |
| `2` | 6263 |
| `3` | 3860 |
| `4` | 2428 |
| `5` | 1484 |
| `6` | 968 |
| `None` | 610 |
| `7` | 343 |
| `8` | 192 |
| `9` | 105 |
| `10` | 95 |
| `11` | 46 |
| `12` | 35 |
| `13` | 9 |
| `15` | 8 |
| `17` | 7 |
| `14` | 5 |
| `18` | 2 |
| `20` | 1 |
| `19` | 1 |
