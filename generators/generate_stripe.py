#!/usr/bin/env python3
"""Genera charges de Stripe test mode para los pedidos nuevos de Postgres (Fase 2).

Selecciona los pedidos más recientes -- los que generate_orders.py inserta con
fecha actual, distinguibles de los ~99k pedidos históricos de Olist (2016-2018)
por año de compra -- y crea un charge por cada uno, con `metadata.order_id`
apuntando al pedido en Postgres. Usa el order_id como idempotency key de Stripe,
así que correr el script varias veces sobre los mismos pedidos no duplica charges.
"""

import argparse
import os
import sys

import psycopg2
import stripe
from dotenv import load_dotenv

# Olist real cubre 2016-2018; cualquier pedido posterior es del generador de Fase 1.
OLIST_HISTORICAL_CUTOFF = "2019-01-01"


def connect_postgres():
    password = os.environ.get("POSTGRES_PASSWORD")
    if not password:
        sys.exit("POSTGRES_PASSWORD no está definido -- completá .env primero.")
    return psycopg2.connect(
        host="localhost",
        port=5434,
        dbname="olist",
        user="airbyte_reader",
        password=password,
    )


def fetch_recent_orders(cur, limit: int):
    cur.execute(
        """
        SELECT o.order_id, p.payment_value
        FROM orders o
        JOIN order_payments p ON p.order_id = o.order_id
        WHERE o.order_purchase_timestamp >= %s
        ORDER BY o.order_purchase_timestamp DESC
        LIMIT %s
        """,
        (OLIST_HISTORICAL_CUTOFF, limit),
    )
    return cur.fetchall()


def create_charge(order_id: str, payment_value) -> str:
    amount_cents = int(round(float(payment_value) * 100))
    charge = stripe.Charge.create(
        amount=amount_cents,
        currency="brl",
        source="tok_visa",  # token de test de Stripe, siempre válido en test mode
        description=f"Pedido {order_id}",
        metadata={"order_id": order_id},
        idempotency_key=order_id,
    )
    return charge.id


def main() -> None:
    load_dotenv()
    stripe_key = os.environ.get("STRIPE_API_KEY")
    if not stripe_key:
        sys.exit("STRIPE_API_KEY no está definido -- completá .env primero.")
    stripe.api_key = stripe_key

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Pedidos recientes a facturar en Stripe (default 10)",
    )
    args = parser.parse_args()

    conn = connect_postgres()
    try:
        with conn:
            with conn.cursor() as cur:
                orders = fetch_recent_orders(cur, args.limit)
    finally:
        conn.close()

    for order_id, payment_value in orders:
        charge_id = create_charge(order_id, payment_value)
        print(f"{order_id} -> {charge_id}")
    print(f"Charges procesados: {len(orders)}")


if __name__ == "__main__":
    main()
