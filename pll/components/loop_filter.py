import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config import R, C1, C2


def lf_derivatives(Vtune, vC1, Icp_signed):
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
    dvC1_dt   = (Vtune - vC1) / (R * C1)
    return dVtune_dt, dvC1_dt
