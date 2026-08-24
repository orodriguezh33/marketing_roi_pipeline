"""Exporta un snapshot local (Parquet) de los marts + tablas de staging clave
de MotherDuck, para que los notebooks de analyst_portfolio/ corran sin
credenciales ni conexión a internet.

Uso:
    uv run python analyst_portfolio/export_data.py

Requiere MOTHERDUCK_TOKEN en el .env de la raíz del repo (mismo token que usa
dbt, ver docs/setup/fase3-instalacion.md). El snapshot resultante en
analyst_portfolio/data/raw/ SÍ se commitea -- es lo que hace que el
portafolio sea reproducible sin acceso al warehouse real.
"""

from __future__ import annotations

import os
from pathlib import Path

import duckdb
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = Path(__file__).resolve().parent / "data" / "raw"

# database.schema.table -> nombre de archivo parquet de salida
TABLES = {
    "marketing_roi.marts.fct_orders": "fct_orders",
    "marketing_roi.marts.fct_marketing_performance": "fct_marketing_performance",
    "marketing_roi.marts.dim_customer": "dim_customer",
    "marketing_roi.marts.dim_product": "dim_product",
    "marketing_roi.marts.dim_channel": "dim_channel",
    "marketing_roi.marts.dim_date": "dim_date",
    "marketing_roi.staging.stg_postgres__order_items": "stg_order_items",
    "marketing_roi.staging.stg_postgres__order_reviews": "stg_order_reviews",
}


def _select_with_decimals_as_double(
    con: duckdb.DuckDBPyConnection, qualified_name: str
) -> str:
    """DECIMAL columns land as Python `Decimal` (dtype `object`) in pandas,
    which breaks numpy ops like `.quantile()`. Cast them to DOUBLE at export
    time so every notebook gets plain float64 columns."""
    columns = con.execute(f"DESCRIBE {qualified_name}").fetchall()
    select_list = ", ".join(
        (
            f'CAST("{name}" AS DOUBLE) AS "{name}"'
            if dtype.startswith("DECIMAL")
            else f'"{name}"'
        )
        for name, dtype, *_ in columns
    )
    return f"SELECT {select_list} FROM {qualified_name}"


def main() -> None:
    load_dotenv(REPO_ROOT / ".env")
    os.environ["motherduck_token"] = os.environ["MOTHERDUCK_TOKEN"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect("md:")

    for qualified_name, filename in TABLES.items():
        out_path = OUTPUT_DIR / f"{filename}.parquet"
        select_sql = _select_with_decimals_as_double(con, qualified_name)
        con.execute(
            f"COPY ({select_sql}) TO '{out_path}' (FORMAT PARQUET, COMPRESSION ZSTD)"
        )
        result = con.execute(f"SELECT count(*) FROM {qualified_name}").fetchone()
        rows = result[0] if result else 0
        print(f"{qualified_name} -> {out_path.relative_to(REPO_ROOT)} ({rows:,} filas)")

    con.close()


if __name__ == "__main__":
    main()
