# Profiling: `raw_postgres.orders`

Generado: 2026-08-23 14:17 UTC

- **Filas**: 99491
- **Clave candidata**: `order_id` — sin duplicados

## Columnas

| Columna | Tipo | % nulls | Cardinalidad | Min | Max |
|---|---|---|---|---|---|
| `order_id` | VARCHAR | 0.0% | 99491 | — | — |
| `customer_id` | VARCHAR | 0.0% | 99441 | — | — |
| `order_status` | VARCHAR | 0.0% | 8 | — | — |
| `order_approved_at` | TIMESTAMP | 0.21% | 90733 | 2016-09-15 12:16:38 | 2018-09-03 17:40:06 |
| `order_purchase_timestamp` | TIMESTAMP | 0.0% | 98878 | 2016-09-04 21:15:19 | 2026-08-21 15:16:01.108686 |
| `order_delivered_carrier_date` | TIMESTAMP | 1.84% | 81024 | 2016-10-08 10:34:01 | 2026-08-21 15:16:01.622873 |
| `order_delivered_customer_date` | TIMESTAMP | 3.01% | 95683 | 2016-10-11 13:46:32 | 2026-08-21 15:16:01.624106 |
| `order_estimated_delivery_date` | TIMESTAMP | 0.0% | 462 | 2016-09-30 00:00:00 | 2026-08-28 15:16:01.108686 |
| `_airbyte_extracted_at` | TIMESTAMP | 0.0% | 99491 | 2026-08-21 20:29:58.338380 | 2026-08-21 20:30:13.659648 |

## Frecuencia de valores (columnas de baja cardinalidad)

### `order_status`

| Valor | Filas |
|---|---|
| `delivered` | 96497 |
| `shipped` | 1094 |
| `canceled` | 625 |
| `unavailable` | 609 |
| `invoiced` | 314 |
| `processing` | 295 |
| `created` | 55 |
| `approved` | 2 |
