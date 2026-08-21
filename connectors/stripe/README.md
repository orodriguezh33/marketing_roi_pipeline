# Stripe — `stripe-marketing-roi`

Pagos "modernos" post-migración: charges de test creados por
`generators/generate_stripe.py`, uno por cada pedido nuevo de
`generate_orders.py`, con `metadata.order_id` como vínculo hacia Postgres.

## Source

- Tipo: **Stripe**.
- Account ID: campo **obligatorio** en este conector (no se puede dejar vacío aunque
  no se use Stripe Connect) — tiene que ser el `acct_...` de la cuenta **dueña de la
  key**, no cualquier cuenta activa en el dashboard.
- Secret key: `STRIPE_API_KEY` de `.env` (test mode).
- Streams: solo `charges`. Sync mode: **Incremental**.

## Destination

- `motherduck-raw-stripe` → `md:marketing_roi`, `schema = raw_stripe`.

## Troubleshooting

**Sync "termina bien" pero `charges` queda en 0 filas** — si hay más de un
workspace/cuenta de Stripe bajo el mismo login, es fácil copiar el Account ID de la
cuenta equivocada desde **Settings → Account details** sin notar en cuál se está
parado (selector de cuenta arriba a la izquierda, al lado del logo). Cuando el
Account ID no coincide con la cuenta de la key, Stripe no tira un error: el conector
loguea `Only Stripe Connect platforms can work with other accounts...` y sigue como
si nada, así que el job de Airbyte queda `Completed`, `Failures: []`, pero con
`recordsSynced: 0`. Verificar el Account ID real de la key así:

```bash
STRIPE_KEY=$(grep '^STRIPE_API_KEY=' .env | cut -d= -f2-)
curl -s https://api.stripe.com/v1/account -u "${STRIPE_KEY}:" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])"
```

Ese `acct_...` es el único válido para esa key — pegarlo tal cual en el campo Account
ID de la Source y volver a sincronizar.

## Estado

Verificado en MotherDuck: `raw_stripe.charges` con 20 filas (job de sync
`replication-job-30`, `Failures: []`).
