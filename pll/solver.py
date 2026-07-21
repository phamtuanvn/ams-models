from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

from .components.loop_filter import lf_derivatives
from .components.vco import vco_dphi_dt

_FLOAT_ZERO = 1e-15


def _odes(t: float, y: list[float], Icp_signed: float) -> list[float]:
    """
    Full ODE system. y = [phi_vco, Vtune, vC1].
    Vtune enters VCO continuously — not held constant during CP phase.
    """
    _, Vtune, vC1 = y

    dphi_dt = vco_dphi_dt(Vtune)
    dVtune_dt, dvC1_dt = lf_derivatives(Vtune, vC1, Icp_signed)

    return [dphi_dt, dVtune_dt, dvC1_dt]


def sim_one_cycle(
    state: NDArray[np.float64],
    t_pulse: float,
    Icp_signed: float,
    T_ref: float,
) -> NDArray[np.float64]:
    """
    Simulate one reference period with a 2-phase hybrid ODE.

    Phase 1 [0, t_pulse]:      CP on  (Icp = Icp_signed)
    Phase 2 [t_pulse, T_ref]:  CP off (Icp = 0)

    Uses Radau (implicit, handles stiff filter time constants).
    Returns updated state array [phi_vco, Vtune, vC1].
    """
    y = list(state)

    if t_pulse > _FLOAT_ZERO:
        sol = solve_ivp(
            lambda t, y: _odes(t, y, Icp_signed),
            [0.0, t_pulse], y,
            method='Radau', rtol=1e-8, atol=1e-12, dense_output=False,
        )
        y = sol.y[:, -1].tolist()

    t_off = T_ref - t_pulse
    if t_off > _FLOAT_ZERO:
        sol = solve_ivp(
            lambda t, y: _odes(t, y, 0.0),
            [0.0, t_off], y,
            method='Radau', rtol=1e-8, atol=1e-12, dense_output=False,
        )
        y = sol.y[:, -1].tolist()

    return np.array(y)
