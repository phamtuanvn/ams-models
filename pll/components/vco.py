from __future__ import annotations

from ..config import F_FREE, KVCO, TWO_PI


def vco_dphi_dt(Vtune: float) -> float:
    """Instantaneous VCO phase rate (rad/s)."""
    return TWO_PI * (F_FREE + KVCO * Vtune)
