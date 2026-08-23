#!/usr/bin/env python3
"""Descarga el dataset Olist vía Kaggle API y carga los 9 CSVs a Postgres.

Requiere KAGGLE_USERNAME/KAGGLE_KEY y POSTGRES_PASSWORD en .env, y las tablas ya
creadas (infra/postgres/init/01_schema.sql). El nombre de columnas de cada tabla
coincide con el header real del CSV, así que la carga usa COPY con la lista de
columnas leída del propio archivo -- no depende de que el orden de columnas de la
tabla coincida con el del CSV.
"""

import csv
import os
import sys
from pathlib import Path

import kagglehub
import psycopg2
from dotenv import load_dotenv

DATASET_HANDLE = "olistbr/brazilian-ecommerce"

FILE_TO_TABLE = {
    "olist_customers_dataset.csv": "customers",
    "olist_geolocation_dataset.csv": "geolocation",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_orders_dataset.csv": "orders",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "product_category_name_translation.csv": "product_category_name_translation",
}

# Sin FKs entre estas tablas (ver 01_schema.sql), el orden es solo por legibilidad.
LOAD_ORDER = [
    "product_category_name_translation.csv",
    "olist_customers_dataset.csv",
    "olist_sellers_dataset.csv",
    "olist_products_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
]


def load_csv(cur, csv_path: Path, table: str) -> int:
    # utf-8-sig: algunos CSVs del dataset traen BOM al inicio del primer header.
    with csv_path.open("r", encoding="utf-8-sig") as f:
        header = next(csv.reader(f))
    columns = ", ".join(f'"{c}"' for c in header)
    with csv_path.open("r", encoding="utf-8-sig") as f:
        cur.copy_expert(
            f'COPY "{table}" ({columns}) FROM STDIN WITH (FORMAT csv, HEADER true)',
            f,
        )
    cur.execute(f'SELECT COUNT(*) FROM "{table}"')
    return cur.fetchone()[0]


def main() -> None:
    load_dotenv()

    password = os.environ.get("POSTGRES_PASSWORD")
    if not password:
        sys.exit("POSTGRES_PASSWORD no está definido -- completá .env primero.")
    if not os.environ.get("KAGGLE_USERNAME") or not os.environ.get("KAGGLE_KEY"):
        sys.exit(
            "KAGGLE_USERNAME/KAGGLE_KEY no están definidos -- completá .env primero."
        )

    dataset_dir = Path(kagglehub.dataset_download(DATASET_HANDLE))
    print(f"Dataset descargado en: {dataset_dir}")

    conn = psycopg2.connect(
        host="localhost",
        port=5434,
        dbname="olist",
        user="airbyte_reader",
        password=password,
    )
    try:
        with conn, conn.cursor() as cur:
            for filename in LOAD_ORDER:
                table = FILE_TO_TABLE[filename]
                csv_path = dataset_dir / filename
                if not csv_path.exists():
                    sys.exit(f"No se encontró {filename} en {dataset_dir}")
                rows = load_csv(cur, csv_path, table)
                print(f"{table}: {rows} filas")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
