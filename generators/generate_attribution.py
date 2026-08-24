#!/usr/bin/env python3
"""Genera CSVs de atribución de marketing (order_id -> canal) y los sube a MinIO.

Simula un export de attribution tool (tipo GA4/UTM last-click), que es donde en una
arquitectura real vive la atribución -- ni Postgres ni Stripe traen un campo de canal
en el pedido/pago, así que sin esta fuente `fct_marketing_performance` no tiene forma
de medir revenue/CAC por canal (solo estimarlo repartiendo el spend diario, ver
docs/ROADMAP.md Fase 3 -- Ampliación, decisión #15).

Un archivo por corrida en raw/attribution/attribution_<timestamp>.csv, columnas
order_id,channel,attributed_at,touchpoint. Igual que generate_ads_spend.py, cada
corrida elige al azar un formato de nombre de canal para simular variantes de export
-- la normalización real pasa en dbt staging.

Por cada order_id de Postgres:
1. Con probabilidad UNATTRIBUTED_SHARE no se emite fila -- ese pedido queda
   direct/organic, sin atribuir (ninguna atribución real cubre el 100% del revenue).
2. Si se atribuye, el canal se samplea con un peso por canal (channel_profiles.py) que
   depende de si es el primer pedido de ese customer_unique_id: `acquisition_bias`
   pesa más en primer pedido (motores de adquisición como Google/Facebook) y menos en
   recompra (Email, canal de retención) -- así CAC y ROAS terminan siendo distintos
   por canal, no solo el share de spend.

Por default genera solo la atribución de hoy; con --start-date/--end-date se puede
generar de una el rango histórico completo (2016-2018), igual que
generate_ads_spend.py.
"""

import argparse
import csv
import io
import os
import random
import sys
from datetime import date, datetime

import boto3
import psycopg2
from dotenv import load_dotenv

from channel_profiles import CHANNEL_PROFILES, CHANNEL_VARIANTS, UNATTRIBUTED_SHARE

CHANNELS = list(CHANNEL_PROFILES.keys())


def connect_postgres():
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
        host="localhost", port=port, dbname=dbname, user=user, password=password
    )


def fetch_orders(conn, start: date, end: date) -> list[tuple[str, bool]]:
    """order_id + si es el primer pedido de ese customer_unique_id."""
    with conn.cursor() as cur:
        cur.execute(
            """
            with first_orders as (
                select
                    c.customer_unique_id,
                    min(o.order_purchase_timestamp::date) as first_order_date
                from orders o
                join customers c on o.customer_id = c.customer_id
                group by c.customer_unique_id
            )
            select
                o.order_id,
                o.order_purchase_timestamp::date = fo.first_order_date as is_first_order
            from orders o
            join customers c on o.customer_id = c.customer_id
            join first_orders fo on fo.customer_unique_id = c.customer_unique_id
            where o.order_purchase_timestamp::date between %s and %s
            """,
            (start, end),
        )
        return [(row[0], row[1]) for row in cur.fetchall()]


def channel_weights(is_first_order: bool) -> list[float]:
    weights = []
    for channel in CHANNELS:
        profile = CHANNEL_PROFILES[channel]
        mean_spend = sum(profile.spend_range) / 2
        bias = (
            profile.acquisition_bias if is_first_order else 1 / profile.acquisition_bias
        )
        weights.append(mean_spend * profile.revenue_weight * bias)
    return weights


def build_csv(orders: list[tuple[str, bool]]) -> str:
    variant_index = random.randint(0, 2)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["order_id", "channel", "attributed_at", "touchpoint"])
    for order_id, is_first_order in orders:
        if random.random() < UNATTRIBUTED_SHARE:
            continue
        channel = random.choices(
            CHANNELS, weights=channel_weights(is_first_order), k=1
        )[0]
        variant = CHANNEL_VARIANTS[channel][variant_index]
        writer.writerow([order_id, variant, datetime.now().isoformat(), "last_click"])
    return buffer.getvalue()


def upload(content: str) -> str:
    minio_port = os.environ.get("MINIO_PORT")
    access_key = os.environ.get("MINIO_ROOT_USER")
    secret_key = os.environ.get("MINIO_ROOT_PASSWORD")
    bucket = os.environ.get("MINIO_BUCKET")
    if not all([minio_port, access_key, secret_key, bucket]):
        sys.exit(
            "Faltan variables de MinIO en .env "
            "(MINIO_PORT, MINIO_ROOT_USER, MINIO_ROOT_PASSWORD, MINIO_BUCKET)."
        )

    client = boto3.client(
        "s3",
        endpoint_url=f"http://localhost:{minio_port}",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    key = f"raw/attribution/attribution_{datetime.now():%Y%m%dT%H%M%S}.csv"
    client.put_object(Bucket=bucket, Key=key, Body=content.encode("utf-8"))
    return key


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--start-date",
        type=date.fromisoformat,
        default=date.today(),
        help="YYYY-MM-DD, default hoy",
    )
    parser.add_argument(
        "--end-date",
        type=date.fromisoformat,
        default=date.today(),
        help="YYYY-MM-DD, default hoy",
    )
    args = parser.parse_args()

    conn = connect_postgres()
    try:
        orders = fetch_orders(conn, args.start_date, args.end_date)
    finally:
        conn.close()

    if not orders:
        print("No hay pedidos en ese rango de fechas -- nada que atribuir.")
        return

    content = build_csv(orders)
    key = upload(content)
    print(
        f"{len(orders)} pedidos evaluados. Subido a s3://{os.environ['MINIO_BUCKET']}/{key}"
    )


if __name__ == "__main__":
    main()
