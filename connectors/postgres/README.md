# Postgres — `postgres-olist-cdc`

Fuente transaccional: Postgres local (dataset Olist + `generators/generate_orders.py`),
replicado por CDC.

## Source

- Tipo: **Postgres** (conector `source-postgres:3.8.4`).
- Host: `host.docker.internal` (no `localhost` — Airbyte corre dentro del cluster
  `kind` de `abctl`, no tiene acceso directo al loopback del host).
- Puerto: `POSTGRES_PORT` de `.env` (`5434`).
- Database/user/password: `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD`.
- Replication method: **Logical Replication (CDC)**, publication `airbyte_pub`,
  replication slot `airbyte_slot`. Este conector ya no expone selector de plugin en la
  UI: `wal2json` fue deprecado, `pgoutput` quedó hardcodeado como único plugin.
- Streams: las 9 tablas Olist (`customers`, `orders`, `order_items`, `order_payments`,
  `order_reviews`, `products`, `sellers`, `geolocation`,
  `product_category_name_translation`).

## Destination

- `motherduck-raw-postgres` → `md:marketing_roi`, `schema = raw_postgres`.

## Troubleshooting

**`Replication slot 'airbyte_slot' not found`** — Airbyte solo *verifica* que el slot
exista antes de sincronizar, no lo crea (requiere el privilegio `REPLICATION`, que el
conector no ejerce). El slot se crea junto con la publication en
`infra/postgres/init/02_publication.sql`
(`SELECT pg_create_logical_replication_slot('airbyte_slot', 'pgoutput');`), así que en
una instalación nueva del volumen ya queda creado. Si el error aparece en un volumen
que existía antes de este fix, correrlo a mano una vez:

```bash
docker compose exec -T postgres psql -U airbyte_reader -d olist \
  -c "SELECT pg_create_logical_replication_slot('airbyte_slot', 'pgoutput');"
```

## Estado

Verificado en MotherDuck: `raw_postgres` con las 9 tablas pobladas (`orders` incluye
tanto el histórico Olist como las filas nuevas de `generate_orders.py`).
