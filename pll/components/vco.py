import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config import F_FREE, KVCO, TWO_PI


def vco_dphi_dt(Vtune):
    """Instantaneous VCO phase rate (rad/s)."""
    return TWO_PI * (F_FREE + KVCO * Vtune)
