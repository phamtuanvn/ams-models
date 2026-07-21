from __future__ import annotations

from ..config import C1, C2, R


def lf_derivatives(Vtune: float, vC1: float, Icp_signed: float) -> tuple[float, float]:
    """
    Type-II CP-PLL loop filter ODEs.
    Topology: CP_out --+-- R -- C1 -- GND
                       |
                       C2
                       |
                      GND
    Vtune = V at CP_out node (across C2).

    Returns (dVtune_dt, dvC1_dt).
    """
    dVtune_dt = (Icp_signed - (Vtune - vC1) / R) / C2
    dvC1_dt = (Vtune - vC1) / (R * C1)
    return dVtune_dt, dvC1_dt
