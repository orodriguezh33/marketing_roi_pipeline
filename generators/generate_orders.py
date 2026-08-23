#!/usr/bin/env python3
"""Generador continuo de actividad en Postgres para alimentar CDC (Fase 1/2).

Cada corrida hace dos cosas:
1. Inserta pedidos nuevos (orders + order_items + order_payments), reusando
   customers/products/sellers ya cargados por seed_olist.py.
2. Avanza el estado de pedidos existentes un paso en el camino feliz
   created -> approved -> processing -> shipped -> delivered, actualizando la
   columna de timestamp correspondiente. No toca pedidos 'canceled'/'unavailable'
   ni 'invoiced' (son ramas alternativas del dataset original, no una progresión).

Pensado para correrse repetidas veces (a mano o desde un scheduler en Fase 5) y que
cada corrida deje filas nuevas/modificadas que Airbyte capture vía CDC.
"""

import argparse
import os
import random
import sys
import uuid
from datetime import datetime, timedelta

import psycopg2
from dotenv import load_dotenv

STATUS_PROGRESSION = ["created", "approved", "processing", "shipped", "delivered"]
STATUS_TIMESTAMP_COLUMN = {
    "approved": "order_approved_at",
    "shipped": "order_delivered_carrier_date",
    "delivered": "order_delivered_customer_date",
}
PAYMENT_TYPES = ["credit_card", "boleto", "voucher", "debit_card"]


def connect():
    load_dotenv()
    port = os.environ.get("POSTGRES_PORT")
    dbname = os.environ.get("POSTGRES_DB")
    user = os.environ.get("POSTGRES_USER")
    password = os.environ.get("POSTGRES_PASSWORD")
    if not all([port, dbname, user, password]):
        sys.exit(
            "Faltan variables de Postgres en .env "
            "(POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD)."
        )
    return psycopg2.connect(
        host="localhost",
        port=port,
        dbname=dbname,
        user=user,
        password=password,
    )


def insert_new_orders(cur, count: int) -> int:
    cur.execute(
        "SELECT customer_id FROM customers ORDER BY random() LIMIT %s", (count,)
    )
    customer_ids = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT product_id FROM products ORDER BY random() LIMIT 200")
    product_ids = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT seller_id FROM sellers ORDER BY random() LIMIT 200")
    seller_ids = [row[0] for row in cur.fetchall()]

    now = datetime.now()
    inserted = 0
    for customer_id in customer_ids:
        order_id = uuid.uuid4().hex
        cur.execute(
            """
            INSERT INTO orders (
                order_id, customer_id, order_status,
                order_purchase_timestamp, order_estimated_delivery_date
            ) VALUES (%s, %s, 'created', %s, %s)
            """,
            (order_id, customer_id, now, now + timedelta(days=7)),
        )

        total_value = 0.0
        for item_id in range(1, random.randint(1, 3) + 1):
            price = round(random.uniform(20, 300), 2)
            freight = round(random.uniform(5, 40), 2)
            total_value += price + freight
            cur.execute(
                """
                INSERT INTO order_items (
                    order_id, order_item_id, product_id, seller_id,
                    shipping_limit_date, price, freight_value
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    order_id,
                    item_id,
                    random.choice(product_ids),
                    random.choice(seller_ids),
                    now + timedelta(days=3),
                    price,
                    freight,
                ),
            )

        cur.execute(
            """
            INSERT INTO order_payments (
                order_id, payment_sequential, payment_type,
                payment_installments, payment_value
            ) VALUES (%s, 1, %s, 1, %s)
            """,
            (order_id, random.choice(PAYMENT_TYPES), round(total_value, 2)),
        )
        inserted += 1
    return inserted


def advance_existing_orders(cur, count: int) -> int:
    advanceable = STATUS_PROGRESSION[:-1]  # 'delivered' no tiene siguiente paso
    cur.execute(
        "SELECT order_id, order_status FROM orders WHERE order_status = ANY(%s) "
        "ORDER BY random() LIMIT %s",
        (advanceable, count),
    )
    rows = cur.fetchall()

    updated = 0
    for order_id, current_status in rows:
        next_status = STATUS_PROGRESSION[STATUS_PROGRESSION.index(current_status) + 1]
        timestamp_column = STATUS_TIMESTAMP_COLUMN.get(next_status)
        if timestamp_column:
            cur.execute(
                f"UPDATE orders SET order_status = %s, {timestamp_column} = %s "
                "WHERE order_id = %s",
                (next_status, datetime.now(), order_id),
            )
        else:
            cur.execute(
                "UPDATE orders SET order_status = %s WHERE order_id = %s",
                (next_status, order_id),
            )
        updated += 1
    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--new-orders", type=int, default=10, help="Pedidos nuevos a insertar"
    )
    parser.add_argument(
        "--advance-orders",
        type=int,
        default=5,
        help="Pedidos existentes a avanzar de estado",
    )
    args = parser.parse_args()

    conn = connect()
    try:
        with conn, conn.cursor() as cur:
            inserted = insert_new_orders(cur, args.new_orders)
            updated = advance_existing_orders(cur, args.advance_orders)
        print(f"Pedidos nuevos insertados: {inserted}")
        print(f"Pedidos existentes avanzados de estado: {updated}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
