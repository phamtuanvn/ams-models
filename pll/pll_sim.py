import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import time as walltime

from config import F_REF, F_OUT, N, KVCO, F_FREE, N_CYCLES, T_REF, TWO_PI, ICP_UP, R
from components.pfd import pfd
from solver import sim_one_cycle


def run(mode='pfd', f_free=F_FREE, n_cycles=N_CYCLES, icp=ICP_UP, R=R,
        method='Radau'):
    """
    mode: 'pfd' (tri-state PFD, default) or 'sampled' (±π detector, no
    frequency detection) — see components/pfd.py.
    """
    # Pre-allocate log arrays
    t_arr           = np.empty(n_cycles)
    f_inst_arr      = np.empty(n_cycles)
    Vtune_arr       = np.empty(n_cycles)
    vC1_arr         = np.empty(n_cycles)
    phi_err_raw_arr = np.empty(n_cycles)
    phi_err_pfd_arr = np.empty(n_cycles)
    t_pulse_arr     = np.empty(n_cycles)
    f_avg_arr       = np.empty(n_cycles)
    cycle_slip_times = []

    # "VCO first" ordering: VCO runs → reference edge arrives → PFD fires next cycle.
    # Initial t_pulse = 0 (no info yet), state = all zeros.
    state          = np.array([0.0, 0.0, 0.0])  # [phi_vco, Vtune, vC1]
    phi_ref_accum  = 0.0
    t_pulse        = 0.0
    Icp_signed     = 0.0   # no pulse before first REF edge
    phi_slipped    = 0.0   # phase already dropped by the detector (k·2π)

    for n in range(n_cycles):
        # 1. Log snapshot: state at start of cycle n, t_pulse to be applied this cycle
        t_arr[n]        = n * T_REF * 1e6                         # µs
        f_inst_arr[n]   = (f_free + KVCO * state[1]) / 1e9        # GHz
        Vtune_arr[n]    = state[1] * 1e3                          # mV
        vC1_arr[n]      = state[2] * 1e3                          # mV
        t_pulse_arr[n]  = t_pulse * 1e9                           # ns

        # 2. VCO runs for T_ref with current CP pulse
        phi_start = state[0]
        state = sim_one_cycle(state, t_pulse, Icp_signed, T_REF,
                              f_free=f_free, R=R, method=method)
        # mean VCO frequency over this cycle (free of the CP ripple on Vtune)
        f_avg_arr[n] = (state[0] - phi_start) / (TWO_PI * T_REF) / 1e9   # GHz

        # 3. Reference edge arrives: accumulate one ref cycle
        phi_ref_accum += TWO_PI

        # 4. Compute phase error from phi_vco AFTER this cycle
        phi_fb         = state[0] / N
        phi_err_raw    = phi_ref_accum - phi_fb

        # 5. PFD: decide CP for NEXT cycle
        prev_slipped = phi_slipped
        t_pulse, Icp_signed, phi_err_pfd, phi_slipped = pfd(
            phi_err_raw, phi_slipped, mode, icp, icp)

        # 6. Cycle slip = the detector drops 2π (its error jumps back by one cycle)
        n_new = int(round((phi_slipped - prev_slipped) / TWO_PI))
        cycle_slip_times += [(n + 1) * T_REF * 1e6] * abs(n_new)

        # 7. Log phase error (computed after ODE, before next cycle)
        phi_err_raw_arr[n] = phi_err_raw / TWO_PI   # cycles
        phi_err_pfd_arr[n] = phi_err_pfd             # rad

    return {
        't':               t_arr,
        'f_inst':          f_inst_arr,
        'f_avg':           f_avg_arr,
        'Vtune':           Vtune_arr,
        'vC1':             vC1_arr,
        'phi_err_raw':     phi_err_raw_arr,
        'phi_err_pfd':     phi_err_pfd_arr,
        't_pulse':         t_pulse_arr,
        'cycle_slip_times': cycle_slip_times,
        'Vtune_lock':      (F_OUT - f_free) / KVCO * 1e3,  # mV
        'T_ref_ns':        T_REF * 1e9,
    }


def lock_time(data, f_free=F_FREE, band=0.02):
    """First time after which the cycle-mean VCO frequency stays within ±band
    of the initial offset."""
    df = abs(F_OUT - f_free)
    out = np.where(np.abs(data['f_avg'] * 1e9 - F_OUT) > band * df)[0]
    if len(out) == 0:
        return 0.0
    if out[-1] == len(data['t']) - 1:
        return float('nan')                      # not locked within the run
    return data['t'][out[-1] + 1]


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'pfd'
    print(f"PLL transient sim ({mode}): {N_CYCLES} cycles, F_FREE={F_FREE/1e9:.3f} GHz, "
          f"F_OUT={F_OUT/1e9:.3f} GHz, df={abs(F_OUT-F_FREE)/1e6:.0f} MHz")

    t0 = walltime.time()
    data = run(mode)
    elapsed = walltime.time() - t0

    print(f"Done in {elapsed:.1f}s.")
    print(f"Cycle slips: {len(data['cycle_slip_times'])} "
          f"at t = {[f'{x:.2f}' for x in data['cycle_slip_times']]} us")
    print(f"Lock (±2% of df): {lock_time(data):.2f} us")
    print(f"Final: f_inst={data['f_inst'][-1]:.5f} GHz  "
          f"Vtune={data['Vtune'][-1]:.2f} mV  (target {data['Vtune_lock']:.1f} mV)")

    import plot
    plot.make_plots(data)
