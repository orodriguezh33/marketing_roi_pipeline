"""Tests para el sampler de canal de generate_attribution.py.

Esto es lo que le da forma a la tensión ROAS-vs-CAC del análisis: si los pesos no
favorecen a Email en revenue y a Google en adquisición de clientes nuevos, todo el
punto de reemplazar la atribución proporcional por una medida se pierde.
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "generators"))

from generate_attribution import CHANNELS, build_csv, channel_weights


def test_channel_weights_favor_email_on_repeat_orders():
    weights = dict(zip(CHANNELS, channel_weights(is_first_order=False)))

    assert weights["Email Marketing"] == max(weights.values())


def test_channel_weights_favor_google_on_first_orders():
    weights = dict(zip(CHANNELS, channel_weights(is_first_order=True)))

    assert weights["Google Ads"] == max(weights.values())


def test_channel_weights_flip_ranking_between_first_and_repeat_orders():
    first_order_weights = dict(zip(CHANNELS, channel_weights(is_first_order=True)))
    repeat_order_weights = dict(zip(CHANNELS, channel_weights(is_first_order=False)))

    assert (
        first_order_weights["Google Ads"] / first_order_weights["Email Marketing"]
        > repeat_order_weights["Google Ads"] / repeat_order_weights["Email Marketing"]
    )


def test_build_csv_leaves_a_share_of_orders_unattributed():
    random.seed(0)
    orders = [(f"order-{i}", False) for i in range(2000)]

    csv_text = build_csv(orders)

    attributed_rows = csv_text.strip().splitlines()[1:]
    unattributed_share = 1 - (len(attributed_rows) / len(orders))
    assert 0.04 < unattributed_share < 0.12


def test_build_csv_only_uses_known_order_ids():
    random.seed(1)
    orders = [("order-a", True), ("order-b", False)]

    csv_text = build_csv(orders)

    rows = csv_text.strip().splitlines()[1:]
    order_ids = {row.split(",")[0] for row in rows}
    assert order_ids <= {"order-a", "order-b"}
