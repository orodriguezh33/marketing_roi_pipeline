"""Tests para generate_stripe.py (checklist QA 2026-08-23, item 'Sin tests unitarios
de Python'): la dedup vía idempotency_key es lo que evita duplicar charges si el
generador se corre dos veces sobre los mismos pedidos -- un bug ahí duplicaría cargos
reales (aunque sea en test mode) sin que dbt/GE lo detecten como error, solo como un
número raro de charges por pedido.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "generators"))

from generate_stripe import (
    OLIST_HISTORICAL_CUTOFF,
    create_charge,
    fetch_recent_orders,
)


def test_create_charge_uses_order_id_as_idempotency_key():
    with patch("generate_stripe.stripe") as mock_stripe:
        mock_stripe.Charge.create.return_value = MagicMock(id="ch_123")

        charge_id = create_charge("order-abc", payment_value=19.9)

        assert charge_id == "ch_123"
        _args, kwargs = mock_stripe.Charge.create.call_args
        assert kwargs["idempotency_key"] == "order-abc"
        assert kwargs["metadata"] == {"order_id": "order-abc"}


def test_create_charge_converts_payment_value_to_cents_and_rounds():
    with patch("generate_stripe.stripe") as mock_stripe:
        mock_stripe.Charge.create.return_value = MagicMock(id="ch_456")

        create_charge("order-xyz", payment_value="10.005")

        _args, kwargs = mock_stripe.Charge.create.call_args
        assert kwargs["amount"] == 1000 or kwargs["amount"] == 1001
        assert isinstance(kwargs["amount"], int)


def test_fetch_recent_orders_filters_by_olist_historical_cutoff():
    cur = MagicMock()
    cur.fetchall.return_value = [("order-1", 42.0)]

    rows = fetch_recent_orders(cur, limit=10)

    assert rows == [("order-1", 42.0)]
    _sql, params = cur.execute.call_args.args
    cutoff, limit = params
    assert cutoff == OLIST_HISTORICAL_CUTOFF
    assert limit == 10
