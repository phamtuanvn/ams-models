"""
Cross-check of the per-cycle PFD model (pll_sim.run) against an event-driven
tri-state PFD: UP set by the reference edge, DN set by the divider edge, both
reset at once when both are high (zero reset delay). A slip is a reference edge
that arrives while UP is already high.

Compares slip count and lock time (cycle-mean VCO frequency within ±2% of Δf).
Run: python event_check.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import math
import numpy as np
from scipy.integrate import solve_ivp

from config import F_OUT, N, KVCO, C1, C2, T_REF, TWO_PI, ICP_UP, R
from pll_sim import run, lock_time


def run_event(f_free, icp=ICP_UP, R=R, t_end=4e-6):
    def odes(t, y, I):
        return [TWO_PI * (f_free + KVCO * y[1]),
                (I - (y[1] - y[2]) / R) / C2,
                (y[1] - y[2]) / (R * C1)]

    y = np.zeros(3)
    t, up, dn, n_ref, m_div, slips = 0.0, 0, 0, 1, 1, 0
    t_ref, phi_ref = [0.0], [0.0]
    while t < t_end:
        I = icp * (up - dn)

        def div_edge(tt, yy, I=0.0):
            return yy[0] - m_div * N * TWO_PI
        div_edge.terminal, div_edge.direction = True, 1

        sol = solve_ivp(odes, [t, n_ref * T_REF], y, args=(I,), events=div_edge,
                        method='RK45', rtol=1e-9, atol=1e-12, max_step=2e-9)
        if sol.status == 1:                      # divider edge first
            t, y = sol.t_events[0][0], sol.y_events[0][0]
            m_div += 1
            dn = 1
        else:                                    # reference edge
            t, y = n_ref * T_REF, sol.y[:, -1]
            n_ref += 1
            if up:
                slips += 1
            up = 1
            t_ref.append(t)
            phi_ref.append(y[0])
        if up and dn:
            up = dn = 0
    f_avg = np.diff(phi_ref) / (TWO_PI * T_REF)
    return np.array(t_ref[:-1]), f_avg, slips


if __name__ == '__main__':
    cases = [(300e6, ICP_UP, R), (600e6, ICP_UP, R),
             (300e6, 20e-6, R * math.sqrt(ICP_UP / 20e-6))]
    for df, icp, r in cases:
        f_free = F_OUT - df
        t, fa, s = run_event(f_free, icp, r)
        out = np.where(np.abs(fa - F_OUT) > 0.02 * df)[0]
        tl = t[out[-1] + 1] * 1e6
        d = run('pfd', f_free, 200, icp=icp, R=r)
        print(f"df {df/1e6:.0f} MHz, Icp {icp*1e6:.0f} uA:  event {s} slips, lock {tl:.2f} us"
              f"  |  per-cycle {len(d['cycle_slip_times'])} slips, lock {lock_time(d, f_free):.2f} us")
