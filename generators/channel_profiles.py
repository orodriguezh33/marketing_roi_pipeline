"""Fuente única de verdad para los 4 canales de marketing sintéticos.

Antes de esto, `CHANNELS`/`CHANNEL_VARIANTS` estaban duplicados como literales en
generate_budget.py y generate_ads_spend.py. Ahora generate_ads_spend.py,
generate_attribution.py y generate_budget.py importan de acá, así que el spend, la
atribución y el presupuesto siempre hablan de los mismos 4 canales con las mismas
variantes de formato de export.

`revenue_weight` y `acquisition_bias` son los parámetros que le dan forma a la
tensión ROAS-vs-CAC que generate_attribution.py siembra a propósito: Email tiene
`revenue_weight` alto pero `acquisition_bias` bajo (barato de correr, bueno reteniendo,
malo adquiriendo clientes nuevos); Google es lo opuesto (motor de adquisición, ROAS
más ajustado). Ver docs/ROADMAP.md Fase 3 -- Ampliación (decisión #15) para el
razonamiento completo.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ChannelProfile:
    spend_range: tuple[float, float]
    revenue_weight: float
    acquisition_bias: float
    variants: tuple[str, str, str]


CHANNEL_PROFILES: dict[str, ChannelProfile] = {
    "Google Ads": ChannelProfile(
        spend_range=(1200.0, 2600.0),
        revenue_weight=1.00,
        acquisition_bias=1.6,
        variants=("Google Ads", "google_ads", "GoogleAds"),
    ),
    "Facebook Ads": ChannelProfile(
        spend_range=(900.0, 2100.0),
        revenue_weight=0.85,
        acquisition_bias=1.4,
        variants=("Facebook Ads", "facebook_ads", "FacebookAds"),
    ),
    "Instagram Ads": ChannelProfile(
        spend_range=(500.0, 1400.0),
        revenue_weight=0.70,
        acquisition_bias=1.1,
        variants=("Instagram Ads", "instagram_ads", "InstagramAds"),
    ),
    "Email Marketing": ChannelProfile(
        spend_range=(120.0, 480.0),
        revenue_weight=2.40,
        acquisition_bias=0.15,
        variants=("Email Marketing", "email_marketing", "EmailMarketing"),
    ),
}

CHANNELS = list(CHANNEL_PROFILES.keys())
CHANNEL_VARIANTS = {name: list(p.variants) for name, p in CHANNEL_PROFILES.items()}

# Probabilidad de que un pedido no tenga ningún touchpoint de marketing asociado
# (direct/organic) -- ninguna atribución real cubre el 100% del revenue, y le da al
# análisis un bucket "sin atribuir" honesto en vez de forzar los 4 canales a sumar 100%.
UNATTRIBUTED_SHARE = 0.08
