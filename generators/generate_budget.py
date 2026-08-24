#!/usr/bin/env python3
"""Escribe metas de presupuesto de marketing a Google Sheets (Fase 2).

Sobrescribe por completo la tab `budget` del Sheet "Marketing Budget Targets"
con una fila por mes/canal (columnas month,channel,budget_target) -- pensado
para correrse como "full refresh": cada corrida deja el Sheet consistente sin
importar cuántas veces se haya corrido antes. A diferencia de los CSVs de ads
spend, acá el nombre de canal queda en formato canónico (este Sheet lo mantiene
el equipo de negocio a mano, no un export automático).
"""

import argparse
import os
import random
import sys
from datetime import date

import gspread
from dotenv import load_dotenv

from channel_profiles import CHANNELS

WORKSHEET_NAME = "budget"


def month_range(year: int) -> list[str]:
    return [f"{year}-{month:02d}" for month in range(1, 13)]


def build_rows(year: int) -> list[list]:
    rows = [["month", "channel", "budget_target"]]
    for month in month_range(year):
        for channel in CHANNELS:
            rows.append([month, channel, round(random.uniform(5000, 50000), 2)])
    return rows


def main() -> None:
    load_dotenv()
    credentials_path = os.environ.get("GOOGLE_SHEETS_CREDENTIALS_JSON")
    spreadsheet_id = os.environ.get("GOOGLE_SHEETS_SPREADSHEET_ID")
    if not credentials_path or not spreadsheet_id:
        sys.exit(
            "Faltan GOOGLE_SHEETS_CREDENTIALS_JSON / GOOGLE_SHEETS_SPREADSHEET_ID "
            "en .env."
        )

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--year",
        type=int,
        default=date.today().year,
        help="Año a presupuestar (default el actual)",
    )
    args = parser.parse_args()

    client = gspread.service_account(filename=credentials_path)
    worksheet = client.open_by_key(spreadsheet_id).worksheet(WORKSHEET_NAME)

    rows = build_rows(args.year)
    worksheet.clear()
    worksheet.update(rows)
    print(f"{len(rows) - 1} metas de presupuesto escritas para {args.year}.")


if __name__ == "__main__":
    main()
