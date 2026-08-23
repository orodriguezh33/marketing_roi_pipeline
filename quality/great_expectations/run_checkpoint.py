#!/usr/bin/env python3
"""Corre las suites de Great Expectations sobre los marts en MotherDuck (Fase 4).

Entrypoint simple para que Fase 5 lo invoque via BashOperator (mismo patron que
`dbt run`/`dbt test`). Pull de cada mart a un DataFrame de pandas via
`duckdb.connect('md:...')` -- sin SQLAlchemy/duckdb-engine, mismo mecanismo de
conexion que usa dbt-duckdb (ver dbt/profiles.yml). Sale con codigo != 0 si
alguna expectation falla, para que Airflow marque la task en rojo.
"""

import os
import sys

import duckdb
import great_expectations as gx
from dotenv import load_dotenv
from great_expectations.expectations import (
    ExpectColumnValuesToBeBetween,
)

CONTEXT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATABASE = "md:marketing_roi"

SUITES = {
    "fct_orders_suite": {
        "table": "marts.fct_orders",
        "expectations": [
            ExpectColumnValuesToBeBetween(
                column="payment_value", min_value=0, max_value=None
            ),
            ExpectColumnValuesToBeBetween(
                column="order_value", min_value=0, max_value=None
            ),
            ExpectColumnValuesToBeBetween(
                column="item_count", min_value=1, max_value=None
            ),
        ],
    },
    "fct_marketing_performance_suite": {
        "table": "marts.fct_marketing_performance",
        "expectations": [
            ExpectColumnValuesToBeBetween(column="spend", min_value=0, max_value=10000),
            ExpectColumnValuesToBeBetween(column="roas", min_value=0, max_value=50),
            # mostly=0.98: en dias de muy pocos daily_new_customers (a veces 1
            # para toda la empresa), la formula de atribucion por spend_share
            # en fct_marketing_performance.sql colapsa a
            # total_spend_del_dia / daily_new_customers para cada canal --
            # un artefacto matematico esperado del modelo de atribucion
            # proporcional (ver comentario en ese modelo), no un error de
            # datos. Tolera ese ~2% de dias sin dejar de detectar una
            # regresion real (ej. si el % de outliers crece mucho mas).
            ExpectColumnValuesToBeBetween(
                column="cac", min_value=0, max_value=5000, mostly=0.98
            ),
            ExpectColumnValuesToBeBetween(
                column="spend_share", min_value=0, max_value=1
            ),
        ],
    },
}


def connect_motherduck() -> duckdb.DuckDBPyConnection:
    token = os.getenv("MOTHERDUCK_TOKEN")
    if not token:
        sys.exit("MOTHERDUCK_TOKEN no esta seteado (ver .env.example)")
    os.environ.setdefault("motherduck_token", token)
    return duckdb.connect(DATABASE)


def build_context() -> gx.data_context.FileDataContext:
    context = gx.get_context(mode="file", project_root_dir=CONTEXT_ROOT)
    try:
        context.data_sources.get("marts_pandas")
    except (KeyError, LookupError):
        context.data_sources.add_pandas(name="marts_pandas")
    return context


def get_or_add_suite(context, name: str, expectations: list) -> gx.ExpectationSuite:
    try:
        suite = context.suites.get(name)
        suite.expectations = expectations
        suite.save()
    except (KeyError, gx.exceptions.exceptions.DataContextError):
        suite = context.suites.add(
            gx.ExpectationSuite(name=name, expectations=expectations)
        )
    return suite


def get_or_add_validation_definition(context, name: str, batch_definition, suite):
    try:
        vd = context.validation_definitions.get(name)
    except (KeyError, gx.exceptions.exceptions.DataContextError):
        vd = context.validation_definitions.add(
            gx.ValidationDefinition(name=name, data=batch_definition, suite=suite)
        )
    return vd


def get_or_add_batch_definition(data_asset, name: str):
    try:
        return data_asset.get_batch_definition(name)
    except (KeyError, LookupError):
        return data_asset.add_batch_definition_whole_dataframe(name)


def get_or_add_dataframe_asset(datasource, name: str):
    try:
        return datasource.get_asset(name)
    except (KeyError, LookupError):
        return datasource.add_dataframe_asset(name=name)


def run_suite(
    context, datasource, con: duckdb.DuckDBPyConnection, suite_name: str, config: dict
) -> bool:
    df = con.sql(f"select * from {config['table']}").df()

    asset = get_or_add_dataframe_asset(
        datasource, suite_name.replace("_suite", "_asset")
    )
    batch_definition = get_or_add_batch_definition(
        asset, suite_name.replace("_suite", "_batch")
    )
    suite = get_or_add_suite(context, suite_name, config["expectations"])
    validation_definition = get_or_add_validation_definition(
        context, suite_name.replace("_suite", "_validation"), batch_definition, suite
    )

    result = validation_definition.run(batch_parameters={"dataframe": df})
    print(f"\n=== {suite_name} ({config['table']}, {len(df)} filas) ===")
    print(result.describe())
    return bool(result.success)


def main() -> int:
    load_dotenv()
    con = connect_motherduck()
    context = build_context()
    datasource = context.data_sources.get("marts_pandas")

    results = {
        name: run_suite(context, datasource, con, name, config)
        for name, config in SUITES.items()
    }
    con.close()

    all_passed = all(results.values())
    print("\n=== marts_checkpoint ===")
    for name, passed in results.items():
        print(f"  {name}: {'PASS' if passed else 'FAIL'}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
