# Profiling: `raw_postgres.order_payments`

Generado: 2026-08-23 14:17 UTC

- **Filas**: 103936
- **Clave candidata**: `order_id`, `payment_sequential` — sin duplicados

## Columnas

| Columna | Tipo | % nulls | Cardinalidad | Min | Max |
|---|---|---|---|---|---|
| `order_id` | VARCHAR | 0.0% | 99490 | — | — |
| `payment_type` | VARCHAR | 0.0% | 5 | — | — |
| `payment_value` | DECIMAL(38,9) | 0.0% | 29106 | 0E-9 | 13664.080000000 |
| `payment_sequential` | BIGINT | 0.0% | 29 | 1 | 29 |
| `payment_installments` | BIGINT | 0.0% | 24 | 0 | 24 |
| `_airbyte_extracted_at` | TIMESTAMP | 0.0% | 103936 | 2026-08-21 20:27:07.836432 | 2026-08-21 20:27:27.239276 |

## Frecuencia de valores (columnas de baja cardinalidad)

### `payment_type`

| Valor | Filas |
|---|---|
| `credit_card` | 76809 |
| `boleto` | 19800 |
| `voucher` | 5784 |
| `debit_card` | 1540 |
| `not_defined` | 3 |

### `payment_sequential`

| Valor | Filas |
|---|---|
| `1` | 99410 |
| `2` | 3039 |
| `3` | 581 |
| `4` | 278 |
| `5` | 170 |
| `6` | 118 |
| `7` | 82 |
| `8` | 54 |
| `9` | 43 |
| `10` | 34 |
| `11` | 29 |
| `12` | 21 |
| `13` | 13 |
| `14` | 10 |
| `15` | 8 |
| `16` | 6 |
| `17` | 6 |
| `19` | 6 |
| `18` | 6 |
| `20` | 4 |
| `21` | 4 |
| `22` | 3 |
| `25` | 2 |
| `24` | 2 |
| `23` | 2 |
| `26` | 2 |
| `27` | 1 |
| `29` | 1 |
| `28` | 1 |

### `payment_installments`

| Valor | Filas |
|---|---|
| `1` | 52596 |
| `2` | 12413 |
| `3` | 10461 |
| `4` | 7098 |
| `10` | 5328 |
| `5` | 5239 |
| `8` | 4268 |
| `6` | 3920 |
| `7` | 1626 |
| `9` | 644 |
| `12` | 133 |
| `15` | 74 |
| `18` | 27 |
| `11` | 23 |
| `24` | 18 |
| `20` | 17 |
| `13` | 16 |
| `14` | 15 |
| `17` | 8 |
| `16` | 5 |
| `21` | 3 |
| `0` | 2 |
| `22` | 1 |
| `23` | 1 |
