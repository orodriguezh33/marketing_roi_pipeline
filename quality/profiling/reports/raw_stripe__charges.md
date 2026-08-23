# Profiling: `raw_stripe.charges`

Generado: 2026-08-23 14:17 UTC

- **Filas**: 20
- **Clave candidata**: `id` — sin duplicados

## Columnas

| Columna | Tipo | % nulls | Cardinalidad | Min | Max |
|---|---|---|---|---|---|
| `id` | VARCHAR | 0.0% | 20 | — | — |
| `card` | JSON | 100.0% | — | — | — |
| `paid` | BOOLEAN | 0.0% | 1 | — | — |
| `order` | VARCHAR | 100.0% | 0 | — | — |
| `amount` | BIGINT | 0.0% | 20 | 8103 | 79495 |
| `object` | VARCHAR | 0.0% | 1 | — | — |
| `review` | VARCHAR | 100.0% | 0 | — | — |
| `source` | JSON | 0.0% | — | — | — |
| `status` | VARCHAR | 0.0% | 1 | — | — |
| `created` | BIGINT | 0.0% | 19 | 1787320666 | 1787347324 |
| `dispute` | VARCHAR | 100.0% | 0 | — | — |
| `invoice` | VARCHAR | 100.0% | 0 | — | — |
| `outcome` | JSON | 0.0% | — | — | — |
| `refunds` | JSON | 100.0% | — | — | — |
| `updated` | BIGINT | 0.0% | 18 | 1787320667 | 1787347325 |
| `captured` | BOOLEAN | 0.0% | 1 | — | — |
| `currency` | VARCHAR | 0.0% | 1 | — | — |
| `customer` | VARCHAR | 100.0% | 0 | — | — |
| `disputed` | BOOLEAN | 0.0% | 1 | — | — |
| `livemode` | BOOLEAN | 0.0% | 1 | — | — |
| `metadata` | JSON | 0.0% | — | — | — |
| `refunded` | BOOLEAN | 0.0% | 1 | — | — |
| `shipping` | JSON | 100.0% | — | — | — |
| `application` | VARCHAR | 100.0% | 0 | — | — |
| `description` | VARCHAR | 0.0% | 20 | — | — |
| `destination` | VARCHAR | 100.0% | 0 | — | — |
| `receipt_url` | VARCHAR | 0.0% | 20 | — | — |
| `failure_code` | VARCHAR | 100.0% | 0 | — | — |
| `on_behalf_of` | VARCHAR | 100.0% | 0 | — | — |
| `fraud_details` | JSON | 0.0% | — | — | — |
| `receipt_email` | VARCHAR | 100.0% | 0 | — | — |
| `transfer_data` | JSON | 100.0% | — | — | — |
| `amount_updates` | JSON | 100.0% | — | — | — |
| `payment_intent` | VARCHAR | 100.0% | 0 | — | — |
| `payment_method` | VARCHAR | 0.0% | 20 | — | — |
| `receipt_number` | VARCHAR | 100.0% | 0 | — | — |
| `transfer_group` | VARCHAR | 100.0% | 0 | — | — |
| `amount_captured` | BIGINT | 0.0% | 20 | 8103 | 79495 |
| `amount_refunded` | BIGINT | 0.0% | 1 | 0 | 0 |
| `application_fee` | VARCHAR | 100.0% | 0 | — | — |
| `billing_details` | JSON | 0.0% | — | — | — |
| `failure_message` | VARCHAR | 100.0% | 0 | — | — |
| `source_transfer` | VARCHAR | 100.0% | 0 | — | — |
| `balance_transaction` | VARCHAR | 0.0% | 20 | — | — |
| `statement_descriptor` | VARCHAR | 100.0% | 0 | — | — |
| `statement_description` | VARCHAR | 100.0% | 0 | — | — |
| `application_fee_amount` | BIGINT | 100.0% | 0 | — | — |
| `payment_method_details` | JSON | 0.0% | — | — | — |
| `failure_balance_transaction` | VARCHAR | 100.0% | 0 | — | — |
| `statement_descriptor_suffix` | VARCHAR | 100.0% | 0 | — | — |
| `calculated_statement_descriptor` | VARCHAR | 0.0% | 1 | — | — |
| `_airbyte_extracted_at` | TIMESTAMP | 0.0% | 20 | 2026-08-21 21:36:07.301706 | 2026-08-22 17:25:13.181732 |

## Frecuencia de valores (columnas de baja cardinalidad)

### `paid`

| Valor | Filas |
|---|---|
| `True` | 20 |

### `order`

| Valor | Filas |
|---|---|
| `None` | 20 |

### `object`

| Valor | Filas |
|---|---|
| `charge` | 20 |

### `review`

| Valor | Filas |
|---|---|
| `None` | 20 |

### `status`

| Valor | Filas |
|---|---|
| `succeeded` | 20 |

### `created`

| Valor | Filas |
|---|---|
| `1787347323` | 2 |
| `1787320672` | 1 |
| `1787347316` | 1 |
| `1787347320` | 1 |
| `1787320666` | 1 |
| `1787320671` | 1 |
| `1787347317` | 1 |
| `1787347318` | 1 |
| `1787320667` | 1 |
| `1787347319` | 1 |
| `1787347321` | 1 |
| `1787320673` | 1 |
| `1787347324` | 1 |
| `1787320668` | 1 |
| `1787320674` | 1 |
| `1787320669` | 1 |
| `1787347322` | 1 |
| `1787320670` | 1 |
| `1787320675` | 1 |

### `dispute`

| Valor | Filas |
|---|---|
| `None` | 20 |

### `invoice`

| Valor | Filas |
|---|---|
| `None` | 20 |

### `updated`

| Valor | Filas |
|---|---|
| `1787347320` | 2 |
| `1787320673` | 2 |
| `1787347321` | 1 |
| `1787320667` | 1 |
| `1787347323` | 1 |
| `1787347325` | 1 |
| `1787347317` | 1 |
| `1787320668` | 1 |
| `1787347324` | 1 |
| `1787320675` | 1 |
| `1787320672` | 1 |
| `1787320671` | 1 |
| `1787347318` | 1 |
| `1787320674` | 1 |
| `1787320670` | 1 |
| `1787347319` | 1 |
| `1787347322` | 1 |
| `1787320669` | 1 |

### `captured`

| Valor | Filas |
|---|---|
| `True` | 20 |

### `currency`

| Valor | Filas |
|---|---|
| `brl` | 20 |

### `customer`

| Valor | Filas |
|---|---|
| `None` | 20 |

### `disputed`

| Valor | Filas |
|---|---|
| `False` | 20 |

### `livemode`

| Valor | Filas |
|---|---|
| `False` | 20 |

### `refunded`

| Valor | Filas |
|---|---|
| `False` | 20 |

### `application`

| Valor | Filas |
|---|---|
| `None` | 20 |

### `destination`

| Valor | Filas |
|---|---|
| `None` | 20 |

### `failure_code`

| Valor | Filas |
|---|---|
| `None` | 20 |

### `on_behalf_of`

| Valor | Filas |
|---|---|
| `None` | 20 |

### `receipt_email`

| Valor | Filas |
|---|---|
| `None` | 20 |

### `payment_intent`

| Valor | Filas |
|---|---|
| `None` | 20 |

### `receipt_number`

| Valor | Filas |
|---|---|
| `None` | 20 |

### `transfer_group`

| Valor | Filas |
|---|---|
| `None` | 20 |

### `amount_refunded`

| Valor | Filas |
|---|---|
| `0` | 20 |

### `application_fee`

| Valor | Filas |
|---|---|
| `None` | 20 |

### `failure_message`

| Valor | Filas |
|---|---|
| `None` | 20 |

### `source_transfer`

| Valor | Filas |
|---|---|
| `None` | 20 |

### `statement_descriptor`

| Valor | Filas |
|---|---|
| `None` | 20 |

### `statement_description`

| Valor | Filas |
|---|---|
| `None` | 20 |

### `application_fee_amount`

| Valor | Filas |
|---|---|
| `None` | 20 |

### `failure_balance_transaction`

| Valor | Filas |
|---|---|
| `None` | 20 |

### `statement_descriptor_suffix`

| Valor | Filas |
|---|---|
| `None` | 20 |

### `calculated_statement_descriptor`

| Valor | Filas |
|---|---|
| `ENTORNO DE PRUEBA DE O` | 20 |
