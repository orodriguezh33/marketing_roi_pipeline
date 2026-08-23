"""Tests para quality/great_expectations/run_checkpoint.py (checklist QA 2026-08-23,
item 'Sin tests unitarios de Python' -- parte pendiente sobre run_checkpoint.py /
run_profiling.py).

El resto del script son wrappers finos sobre la API de Great Expectations / una
conexión real a MotherDuck (no hay lógica de negocio propia que valga mockear en
profundidad); lo que sí es un bug real y silencioso si se rompe es que el script
corra sin `MOTHERDUCK_TOKEN` y falle con un traceback críptico en vez del mensaje
claro que se espera desde Airflow.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent / "quality" / "great_expectations")
)

from run_checkpoint import SUITES, connect_motherduck


def test_connect_motherduck_exits_without_token():
    with patch("run_checkpoint.os.getenv", return_value=None):
        try:
            connect_motherduck()
        except SystemExit as exc:
            assert "MOTHERDUCK_TOKEN" in str(exc.code)
        else:
            raise AssertionError("connect_motherduck() no salió sin el token")


def test_connect_motherduck_connects_with_token():
    with (
        patch("run_checkpoint.os.getenv", return_value="fake-token"),
        patch.dict("run_checkpoint.os.environ", {}, clear=False),
        patch("run_checkpoint.duckdb.connect") as mock_connect,
    ):
        mock_connect.return_value = MagicMock()

        connect_motherduck()

        mock_connect.assert_called_once_with("md:marketing_roi")


def test_suites_expectations_reference_expected_tables():
    assert SUITES["fct_orders_suite"]["table"] == "marts.fct_orders"
    assert SUITES["fct_marketing_performance_suite"]["table"] == (
        "marts.fct_marketing_performance"
    )
    for config in SUITES.values():
        assert len(config["expectations"]) > 0
