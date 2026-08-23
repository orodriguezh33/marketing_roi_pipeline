"""Tests para quality/profiling/run_profiling.py (checklist QA 2026-08-23, item
'Sin tests unitarios de Python' -- parte pendiente sobre run_checkpoint.py /
run_profiling.py).

classify/is_excluded/render_report son las funciones puras del script (sin tocar
MotherDuck) y las que determinan qué termina en los reportes committeados en
quality/profiling/reports/ -- un bug ahí produce un reporte con el tipo de columna
mal clasificado o el estado de duplicados mal calculado, silenciosamente.
"""

import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent / "quality" / "profiling")
)

from run_profiling import classify, is_excluded, render_report


def test_classify_numeric_types():
    assert classify("BIGINT") == "numeric"
    assert classify("DECIMAL(10,2)") == "numeric"
    assert classify("double") == "numeric"


def test_classify_temporal_types():
    assert classify("TIMESTAMP") == "temporal"
    assert classify("DATE") == "temporal"


def test_classify_json_and_text():
    assert classify("JSON") == "json"
    assert classify("VARCHAR") == "text"


def test_is_excluded_matches_airbyte_bookkeeping_columns():
    assert is_excluded("_airbyte_raw_id")
    assert is_excluded("_airbyte_meta")
    assert is_excluded("_ab_cdc_deleted_at")
    assert is_excluded("_ab_cdc_updated_at")


def test_is_excluded_leaves_business_columns_alone():
    assert not is_excluded("customer_id")
    assert not is_excluded("order_status")


def test_render_report_without_candidate_key():
    report = render_report(
        schema="raw_postgres",
        table="geolocation",
        row_count=100,
        profiled=[
            {
                "name": "zip_code",
                "type": "VARCHAR",
                "category": "text",
                "nulls": 0,
                "distinct": 90,
                "min": None,
                "max": None,
                "null_pct": 0.0,
            }
        ],
        freq_tables={},
        dup_info=None,
        key_cols=None,
        generated_at="2026-08-23 00:00 UTC",
    )

    assert "ninguna configurada" in report
    assert "`zip_code`" in report
    assert "## Frecuencia de valores" not in report


def test_render_report_flags_duplicates():
    report = render_report(
        schema="raw_postgres",
        table="orders",
        row_count=100,
        profiled=[],
        freq_tables={},
        dup_info=(2, 5),
        key_cols=["order_id"],
        generated_at="2026-08-23 00:00 UTC",
    )

    assert "2 valores de clave duplicados (5 filas extra)" in report


def test_render_report_no_duplicates():
    report = render_report(
        schema="raw_postgres",
        table="orders",
        row_count=100,
        profiled=[],
        freq_tables={},
        dup_info=(0, 0),
        key_cols=["order_id"],
        generated_at="2026-08-23 00:00 UTC",
    )

    assert "sin duplicados" in report


def test_render_report_includes_frequency_tables_when_present():
    report = render_report(
        schema="raw_s3",
        table="ads_spend",
        row_count=10,
        profiled=[],
        freq_tables={"channel": [("google_ads", 6), ("meta_ads", 4)]},
        dup_info=None,
        key_cols=None,
        generated_at="2026-08-23 00:00 UTC",
    )

    assert "## Frecuencia de valores" in report
    assert "`google_ads`" in report
