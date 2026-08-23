# Profiling: `raw_postgres.order_reviews`

Generado: 2026-08-23 14:17 UTC

- **Filas**: 99224
- **Clave candidata**: `review_id` — **789 valores de clave duplicados (814 filas extra)**

## Columnas

| Columna | Tipo | % nulls | Cardinalidad | Min | Max |
|---|---|---|---|---|---|
| `order_id` | VARCHAR | 0.0% | 98673 | — | — |
| `review_id` | VARCHAR | 0.0% | 98410 | — | — |
| `review_score` | BIGINT | 0.0% | 5 | 1 | 5 |
| `review_comment_title` | VARCHAR | 88.34% | 4527 | — | — |
| `review_creation_date` | TIMESTAMP | 0.0% | 636 | 2016-10-02 00:00:00 | 2018-08-31 00:00:00 |
| `review_comment_message` | VARCHAR | 58.7% | 36159 | — | — |
| `review_answer_timestamp` | TIMESTAMP | 0.0% | 98248 | 2016-10-07 18:32:28 | 2018-10-29 12:27:35 |
| `_airbyte_extracted_at` | TIMESTAMP | 0.0% | 99224 | 2026-08-22 17:22:56.793455 | 2026-08-22 17:23:20.676499 |

## Frecuencia de valores (columnas de baja cardinalidad)

### `review_score`

| Valor | Filas |
|---|---|
| `5` | 57328 |
| `4` | 19142 |
| `1` | 11424 |
| `3` | 8179 |
| `2` | 3151 |
