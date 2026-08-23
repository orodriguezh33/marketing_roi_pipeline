#!/usr/bin/env python3
"""Perfila las tablas crudas de las 4 fuentes en MotherDuck (Fase 2.5).

Corre antes de tocar cualquier modelo de staging en dbt (Fase 3): para cada
tabla en `raw_postgres`/`raw_stripe`/`raw_s3`/`raw_sheets` calcula row count,
% de nulls y cardinalidad por columna, rango min/max en columnas
numericas/temporales, tabla de frecuencias en columnas de baja cardinalidad, y
duplicados contra una clave candidata (cuando hay una configurada en KEYS).

Escribe un reporte Markdown por tabla en `quality/profiling/reports/` mas un
indice en `_index.md`. Mismo mecanismo de conexion que
`quality/great_expectations/run_checkpoint.py` (duckdb.connect('md:...'),
sin SQLAlchemy). Es una herramienta de discovery para humanos, no un gate de
pipeline -- no se invoca desde el DAG de Airflow (ver decision #7 de esta
fase en docs/ROADMAP.md).
"""

import datetime as dt
import os
import sys

import duckdb
from dotenv import load_dotenv

DATABASE = "md:marketing_roi"
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")

# Columnas internas de Airbyte sin senal de negocio -- se excluyen del
# profiling por columna (no aportan nada mas alla de "existen"). Incluye las
# columnas de bookkeeping del conector CDC de Postgres (`_ab_cdc_*`), que
# quedan 100% null en todas las filas hasta que CDC capture un update/delete
# real y dominarian el "peor % nulls" de cada reporte si se dejaran adentro.
EXCLUDE_COLUMNS = {"_airbyte_raw_id", "_airbyte_meta"}


def is_excluded(column_name: str) -> bool:
    return column_name in EXCLUDE_COLUMNS or column_name.startswith("_ab_cdc_")


# Umbral de cardinalidad para listar tabla de frecuencias de valores.
LOW_CARDINALITY_THRESHOLD = 50

# Clave candidata por tabla, usada solo para el chequeo de duplicados.
# `raw_postgres.geolocation` queda deliberadamente sin entrada (no tiene PK
# propio en el dataset real -- ver Fase 3, decision #9 en docs/ROADMAP.md).
CANDIDATE_KEYS: dict[str, list[str]] = {
    "raw_postgres.customers": ["customer_id"],
    "raw_postgres.orders": ["order_id"],
    "raw_postgres.order_items": ["order_id", "order_item_id"],
    "raw_postgres.order_payments": ["order_id", "payment_sequential"],
    "raw_postgres.order_reviews": ["review_id"],
    "raw_postgres.products": ["product_id"],
    "raw_postgres.sellers": ["seller_id"],
    "raw_postgres.product_category_name_translation": ["product_category_name"],
    "raw_stripe.charges": ["id"],
    "raw_s3.ads_spend": ["date", "channel"],
    "raw_sheets.budget": ["month", "channel"],
}

RAW_SCHEMAS = ["raw_postgres", "raw_stripe", "raw_s3", "raw_sheets"]

NUMERIC_PREFIXES = (
    "BIGINT",
    "INTEGER",
    "SMALLINT",
    "TINYINT",
    "HUGEINT",
    "UBIGINT",
    "UINTEGER",
    "DOUBLE",
    "FLOAT",
    "DECIMAL",
    "REAL",
)
TEMPORAL_PREFIXES = ("DATE", "TIMESTAMP", "TIME")


def connect_motherduck() -> duckdb.DuckDBPyConnection:
    token = os.getenv("MOTHERDUCK_TOKEN")
    if not token:
        sys.exit("MOTHERDUCK_TOKEN no esta seteado (ver .env.example)")
    os.environ.setdefault("motherduck_token", token)
    return duckdb.connect(DATABASE)


def classify(data_type: str) -> str:
    dt_upper = data_type.upper()
    if dt_upper == "JSON":
        return "json"
    if dt_upper.startswith(NUMERIC_PREFIXES):
        return "numeric"
    if dt_upper.startswith(TEMPORAL_PREFIXES):
        return "temporal"
    return "text"


def list_tables(con: duckdb.DuckDBPyConnection) -> list[tuple[str, str]]:
    placeholders = ", ".join(f"'{s}'" for s in RAW_SCHEMAS)
    rows = con.sql(f"""
        select table_schema, table_name
        from information_schema.tables
        where table_schema in ({placeholders})
        order by 1, 2
        """).fetchall()
    return rows


def list_columns(
    con: duckdb.DuckDBPyConnection, schema: str, table: str
) -> list[tuple[str, str]]:
    rows = con.sql(f"""
        select column_name, data_type
        from information_schema.columns
        where table_schema = '{schema}' and table_name = '{table}'
        order by ordinal_position
        """).fetchall()
    return [(name, dtype) for name, dtype in rows if not is_excluded(name)]


def profile_columns(
    con: duckdb.DuckDBPyConnection,
    schema: str,
    table: str,
    columns: list[tuple[str, str]],
) -> tuple[int, list[dict]]:
    exprs = ["count(*) as row_count"]
    for name, dtype in columns:
        category = classify(dtype)
        exprs.append(
            f'sum(case when "{name}" is null then 1 else 0 end) as "{name}__nulls"'
        )
        if category != "json":
            exprs.append(f'count(distinct "{name}") as "{name}__distinct"')
        if category in ("numeric", "temporal"):
            exprs.append(f'min("{name}") as "{name}__min"')
            exprs.append(f'max("{name}") as "{name}__max"')

    sql = f"select {', '.join(exprs)} from {schema}.{table}"
    row = con.sql(sql).fetchone()
    cols_out = [d[0] for d in con.sql(sql).description]
    result = dict(zip(cols_out, row))

    row_count = result["row_count"]
    profiled = []
    for name, dtype in columns:
        category = classify(dtype)
        entry = {
            "name": name,
            "type": dtype,
            "category": category,
            "nulls": result.get(f"{name}__nulls"),
            "distinct": result.get(f"{name}__distinct"),
            "min": result.get(f"{name}__min"),
            "max": result.get(f"{name}__max"),
        }
        entry["null_pct"] = (
            round(100 * entry["nulls"] / row_count, 2) if row_count else 0.0
        )
        profiled.append(entry)
    return row_count, profiled


def value_frequencies(
    con: duckdb.DuckDBPyConnection, schema: str, table: str, column: str
) -> list[tuple]:
    return con.sql(f"""
        select "{column}" as value, count(*) as n
        from {schema}.{table}
        group by 1
        order by n desc
        limit {LOW_CARDINALITY_THRESHOLD}
        """).fetchall()


def duplicate_check(
    con: duckdb.DuckDBPyConnection, schema: str, table: str, key_cols: list[str]
) -> tuple[int, int]:
    key_list = ", ".join(f'"{c}"' for c in key_cols)
    dup_groups, extra_rows = con.sql(f"""
        select count(*), sum(c - 1)
        from (
            select count(*) as c
            from {schema}.{table}
            group by {key_list}
            having count(*) > 1
        )
        """).fetchone()
    return dup_groups or 0, extra_rows or 0


def render_report(
    schema: str,
    table: str,
    row_count: int,
    profiled: list[dict],
    freq_tables: dict[str, list[tuple]],
    dup_info: tuple[int, int] | None,
    key_cols: list[str] | None,
    generated_at: str,
) -> str:
    lines = [
        f"# Profiling: `{schema}.{table}`",
        "",
        f"Generado: {generated_at}",
        "",
        f"- **Filas**: {row_count}",
    ]

    if key_cols is None:
        lines.append(
            "- **Clave candidata**: ninguna configurada (ver `CANDIDATE_KEYS` en `run_profiling.py`)"
        )
    else:
        dup_groups, extra_rows = dup_info
        key_repr = ", ".join(f"`{c}`" for c in key_cols)
        status = (
            "sin duplicados"
            if dup_groups == 0
            else f"**{dup_groups} valores de clave duplicados ({extra_rows} filas extra)**"
        )
        lines.append(f"- **Clave candidata**: {key_repr} — {status}")

    lines += [
        "",
        "## Columnas",
        "",
        "| Columna | Tipo | % nulls | Cardinalidad | Min | Max |",
        "|---|---|---|---|---|---|",
    ]
    for col in profiled:
        distinct = col["distinct"] if col["distinct"] is not None else "—"
        cmin = col["min"] if col["min"] is not None else "—"
        cmax = col["max"] if col["max"] is not None else "—"
        lines.append(
            f"| `{col['name']}` | {col['type']} | {col['null_pct']}% | {distinct} | {cmin} | {cmax} |"
        )

    if freq_tables:
        lines += ["", "## Frecuencia de valores (columnas de baja cardinalidad)"]
        for col_name, freq in freq_tables.items():
            lines += ["", f"### `{col_name}`", "", "| Valor | Filas |", "|---|---|"]
            for value, n in freq:
                lines.append(f"| `{value}` | {n} |")

    return "\n".join(lines) + "\n"


def main() -> int:
    load_dotenv()
    con = connect_motherduck()
    os.makedirs(REPORTS_DIR, exist_ok=True)
    generated_at = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC")

    index_rows = []
    for schema, table in list_tables(con):
        full_name = f"{schema}.{table}"
        columns = list_columns(con, schema, table)
        row_count, profiled = profile_columns(con, schema, table, columns)

        freq_tables = {}
        for col in profiled:
            # distinct < row_count descarta columnas efectivamente unicas (ids,
            # urls, timestamps de alta precision) que en tablas chicas caerian
            # igual bajo el umbral de cardinalidad sin aportar una distribucion real.
            if (
                col["category"] != "json"
                and col["distinct"] is not None
                and col["distinct"] <= LOW_CARDINALITY_THRESHOLD
                and col["distinct"] < row_count
            ):
                freq_tables[col["name"]] = value_frequencies(
                    con, schema, table, col["name"]
                )

        key_cols = CANDIDATE_KEYS.get(full_name)
        dup_info = duplicate_check(con, schema, table, key_cols) if key_cols else None

        report = render_report(
            schema,
            table,
            row_count,
            profiled,
            freq_tables,
            dup_info,
            key_cols,
            generated_at,
        )
        report_filename = f"{schema}__{table}.md"
        with open(os.path.join(REPORTS_DIR, report_filename), "w") as f:
            f.write(report)

        worst_null = max((c["null_pct"] for c in profiled), default=0.0)
        dup_flag = "—"
        if dup_info is not None:
            dup_flag = "OK" if dup_info[0] == 0 else f"{dup_info[0]} dups"
        index_rows.append((full_name, row_count, dup_flag, worst_null, report_filename))
        print(
            f"  {full_name}: {row_count} filas, peor % nulls = {worst_null}%, dedup = {dup_flag}"
        )

    con.close()

    index_lines = [
        "# Indice de profiling — fuentes crudas",
        "",
        f"Generado: {generated_at}",
        "",
        "| Tabla | Filas | Dedup (clave candidata) | Peor % nulls | Reporte |",
        "|---|---|---|---|---|",
    ]
    for full_name, row_count, dup_flag, worst_null, filename in index_rows:
        index_lines.append(
            f"| `{full_name}` | {row_count} | {dup_flag} | {worst_null}% | [{filename}](./{filename}) |"
        )

    with open(os.path.join(REPORTS_DIR, "_index.md"), "w") as f:
        f.write("\n".join(index_lines) + "\n")

    print(f"\n{len(index_rows)} tablas perfiladas. Reportes en {REPORTS_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
