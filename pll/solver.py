import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from scipy.integrate import solve_ivp
from config import F_FREE, KVCO, R, C1, C2, TWO_PI


def _odes(t, y, Icp_signed, f_free, R):
    """
    Full ODE system. y = [phi_vco, Vtune, vC1].
    Vtune enters VCO continuously — not held constant during CP phase.
    """
    phi_vco, Vtune, vC1 = y

    dphi_dt   = TWO_PI * (f_free + KVCO * Vtune)
    dVtune_dt = (Icp_signed - (Vtune - vC1) / R) / C2
    dvC1_dt   = (Vtune - vC1) / (R * C1)

    return [dphi_dt, dVtune_dt, dvC1_dt]


def sim_one_cycle(state, t_pulse, Icp_signed, T_ref, f_free=F_FREE, R=R,
                  method='Radau'):
    """
    Simulate one reference period with a 2-phase hybrid ODE.

    Phase 1 [0, t_pulse]:      CP on  (Icp = Icp_signed)
    Phase 2 [t_pulse, T_ref]:  CP off (Icp = 0)

    Radau (implicit) by default. R*C2 = 24 ns and R*C1 = 240 ns are only 10x
    apart, so the system is not really stiff and RK45 gives the same result;
    Radau is kept as the safe choice when C2 is made much smaller.
    Returns updated state array [phi_vco, Vtune, vC1].
    """
    y = list(state)

    # Phase 1: CP on
    if t_pulse > 1e-15:
        sol = solve_ivp(
            lambda t, y: _odes(t, y, Icp_signed, f_free, R),
            [0.0, t_pulse], y,
            method=method, rtol=1e-8, atol=1e-12, dense_output=False,
        )
        y = sol.y[:, -1].tolist()

    # Phase 2: CP off
    t_off = T_ref - t_pulse
    if t_off > 1e-15:
        sol = solve_ivp(
            lambda t, y: _odes(t, y, 0.0, f_free, R),
            [0.0, t_off], y,
            method=method, rtol=1e-8, atol=1e-12, dense_output=False,
        )
        y = sol.y[:, -1].tolist()

    return np.array(y)
