"""Tests para la progresión de estados de generate_orders.py (checklist QA 2026-08-23,
item 'Sin tests unitarios de Python').

advance_existing_orders es la lógica más riesgosa del generador: un bug acá produce
transiciones de estado inválidas o timestamps sin setear que romperían silenciosamente
los tests de dbt (ver docs/ROADMAP.md) en vez de fallar rápido en el generador.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "generators"))

from generate_orders import STATUS_PROGRESSION, advance_existing_orders


def make_cursor(rows):
    cur = MagicMock()
    cur.fetchall.return_value = rows
    return cur


def test_advance_orders_moves_each_status_one_step_forward():
    rows = [("order-1", "created"), ("order-2", "approved"), ("order-3", "shipped")]
    cur = make_cursor(rows)

    updated = advance_existing_orders(cur, count=3)

    assert updated == 3
    update_calls = [
        c for c in cur.execute.call_args_list if "UPDATE orders" in c.args[0]
    ]
    assert len(update_calls) == 3

    new_statuses = {call.args[1][0] for call in update_calls}
    assert new_statuses == {"approved", "processing", "delivered"}


def test_advance_orders_sets_timestamp_column_when_one_exists():
    cur = make_cursor([("order-1", "created")])

    advance_existing_orders(cur, count=1)

    sql, params = cur.execute.call_args.args
    assert "order_approved_at" in sql
    next_status, _timestamp, order_id = params
    assert next_status == "approved"
    assert order_id == "order-1"


def test_advance_orders_skips_timestamp_column_for_processing():
    # approved -> processing no tiene columna de timestamp propia en el schema de
    # Olist (STATUS_TIMESTAMP_COLUMN no incluye "processing") -- confirma que el
    # generador no intenta escribir una columna que no existe.
    cur = make_cursor([("order-1", "approved")])

    advance_existing_orders(cur, count=1)

    sql, params = cur.execute.call_args.args
    assert "UPDATE orders SET order_status = %s WHERE order_id = %s" == sql
    assert params == ("processing", "order-1")


def test_advance_orders_never_advances_terminal_or_branch_statuses():
    # 'delivered' es terminal y 'canceled'/'unavailable'/'invoiced' son ramas
    # alternativas del dataset original -- el SELECT en advance_existing_orders
    # filtra con STATUS_PROGRESSION[:-1], así que nunca deberían llegar acá. Este
    # test documenta esa invariante fijándose en el propio WHERE del SELECT.
    cur = make_cursor([])

    advance_existing_orders(cur, count=5)

    _select_sql, select_params = cur.execute.call_args_list[0].args
    advanceable_statuses = select_params[0]
    assert "delivered" not in advanceable_statuses
    assert set(advanceable_statuses) == set(STATUS_PROGRESSION[:-1])
