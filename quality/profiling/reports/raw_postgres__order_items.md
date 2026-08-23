# Profiling: `raw_postgres.order_items`

Generado: 2026-08-23 14:17 UTC

- **Filas**: 112748
- **Clave candidata**: `order_id`, `order_item_id` — sin duplicados

## Columnas

| Columna | Tipo | % nulls | Cardinalidad | Min | Max |
|---|---|---|---|---|---|
| `price` | DECIMAL(38,9) | 0.0% | 6052 | 0.850000000 | 6735.000000000 |
| `order_id` | VARCHAR | 0.0% | 98716 | — | — |
| `seller_id` | VARCHAR | 0.0% | 3095 | — | — |
| `product_id` | VARCHAR | 0.0% | 32951 | — | — |
| `freight_value` | DECIMAL(38,9) | 0.0% | 7001 | 0E-9 | 409.680000000 |
| `order_item_id` | BIGINT | 0.0% | 21 | 1 | 21 |
| `shipping_limit_date` | TIMESTAMP | 0.0% | 93321 | 2016-09-19 00:15:34 | 2026-08-24 15:16:01.108686 |
| `_airbyte_extracted_at` | TIMESTAMP | 0.0% | 112748 | 2026-08-21 20:26:41.081520 | 2026-08-21 20:27:07.831024 |

## Frecuencia de valores (columnas de baja cardinalidad)

### `order_item_id`

| Valor | Filas |
|---|---|
| `1` | 98716 |
| `2` | 9835 |
| `3` | 2303 |
| `4` | 965 |
| `5` | 460 |
| `6` | 256 |
| `7` | 58 |
| `8` | 36 |
| `9` | 28 |
| `10` | 25 |
| `11` | 17 |
| `12` | 13 |
| `13` | 8 |
| `14` | 7 |
| `15` | 5 |
| `17` | 3 |
| `20` | 3 |
| `18` | 3 |
| `16` | 3 |
| `19` | 3 |
| `21` | 1 |
