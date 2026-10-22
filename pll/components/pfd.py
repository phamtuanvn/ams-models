import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from config import F_REF, ICP_UP, ICP_DN, T_REF, TWO_PI


def pfd(phi_err_raw, phi_slipped, mode='pfd', icp_up=ICP_UP, icp_dn=ICP_DN):
    """
    Returns (t_pulse_s, Icp_signed, phi_err_pfd, phi_slipped).
    phi_err_raw: unwrapped accumulated phase error in radians.
    phi_slipped: phase (multiple of 2π) the detector has already dropped
                 through cycle slips; carry it from one call to the next.

    mode='pfd'     tri-state PFD: linear over (-2π, +2π). When the error
                   reaches ±2π one edge is lost: the error drops by 2π
                   but keeps its sign, so the CP keeps pumping the same way.
    mode='sampled' phase detector without frequency detection: error wrapped
                   into (-π, +π], so the CP polarity flips at every wrap.
                   Kept only to show why the PFD needs its ±2π range.

    CP pulse width proportional to |phi_err_pfd|, clamped to T_ref.
    """
    if mode == 'pfd':
        phi_err_pfd = phi_err_raw - phi_slipped
        while phi_err_pfd >= TWO_PI:
            phi_slipped += TWO_PI
            phi_err_pfd -= TWO_PI
        while phi_err_pfd <= -TWO_PI:
            phi_slipped -= TWO_PI
            phi_err_pfd += TWO_PI
    elif mode == 'sampled':
        phi_err_pfd = ((phi_err_raw + np.pi) % TWO_PI) - np.pi
        phi_slipped = phi_err_raw - phi_err_pfd
    else:
        raise ValueError(f"unknown PFD mode {mode!r}")

    t_pulse = abs(phi_err_pfd) / (TWO_PI * F_REF)
    t_pulse = min(t_pulse, T_REF)

    Icp_signed = icp_up if phi_err_pfd >= 0 else -icp_dn

    return t_pulse, Icp_signed, phi_err_pfd, phi_slipped
