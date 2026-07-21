from __future__ import annotations

import numpy as np

from ..config import F_REF, ICP_DN, ICP_UP, T_REF, TWO_PI


def pfd(phi_err_raw: float) -> tuple[float, float, float]:
    """
    Returns (t_pulse_s, Icp_signed, phi_err_pfd).
    phi_err_raw: unwrapped accumulated phase error in radians.

    PFD sees phi_err_pfd = phi_err_raw mod 2π in [-π, π].
    CP pulse width proportional to |phi_err_pfd|, clamped to T_ref.
    """
    phi_err_pfd = ((phi_err_raw + np.pi) % TWO_PI) - np.pi

    t_pulse = abs(phi_err_pfd) / (TWO_PI * F_REF)
    t_pulse = min(t_pulse, T_REF)

    Icp_signed = ICP_UP if phi_err_pfd >= 0 else -ICP_DN

    return t_pulse, Icp_signed, phi_err_pfd
