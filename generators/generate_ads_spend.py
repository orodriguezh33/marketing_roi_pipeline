#!/usr/bin/env python3
"""Genera CSVs de gasto en ads por canal/fecha y los sube a MinIO (Fase 2).

Un archivo por corrida en raw/ads_spend/ads_spend_<timestamp>.csv, columnas
date,channel,spend,currency. Cada corrida elige al azar UN formato de nombre de
canal ("Google Ads" / "google_ads" / "GoogleAds") para todas las filas de ese
archivo -- simula que el formato de export cambia según la plataforma/fecha, a
propósito: la normalización real de canal pasa en dbt staging (Fase 3).

Por default genera solo el gasto de hoy (modo "corrida diaria"); con
--start-date/--end-date se puede generar de una el rango histórico completo
(ej. 2016-2018), para que ROAS tenga con qué compararse en todo el período.
"""

import argparse
import csv
import io
import os
import random
import sys
from datetime import date, datetime, timedelta

import boto3
from dotenv import load_dotenv

CHANNEL_VARIANTS = {
    "Google Ads": ["Google Ads", "google_ads", "GoogleAds"],
    "Facebook Ads": ["Facebook Ads", "facebook_ads", "FacebookAds"],
    "Instagram Ads": ["Instagram Ads", "instagram_ads", "InstagramAds"],
    "Email Marketing": ["Email Marketing", "email_marketing", "EmailMarketing"],
}


def daterange(start: date, end: date):
    for offset in range((end - start).days + 1):
        yield start + timedelta(days=offset)


def build_csv(start: date, end: date) -> str:
    variant_index = random.randint(0, 2)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["date", "channel", "spend", "currency"])
    for day in daterange(start, end):
        for variants in CHANNEL_VARIANTS.values():
            spend = round(random.uniform(200, 3000), 2)
            writer.writerow([day.isoformat(), variants[variant_index], spend, "BRL"])
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
    key = f"raw/ads_spend/ads_spend_{datetime.now():%Y%m%dT%H%M%S}.csv"
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

    content = build_csv(args.start_date, args.end_date)
    key = upload(content)
    print(f"Subido a s3://{os.environ['MINIO_BUCKET']}/{key}")


if __name__ == "__main__":
    main()
