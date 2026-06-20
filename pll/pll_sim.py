import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import time as walltime

from config import F_REF, F_OUT, N, KVCO, F_FREE, N_CYCLES, T_REF, TWO_PI
from components.pfd import pfd
from solver import sim_one_cycle


def run():
    # Pre-allocate log arrays
    t_arr           = np.empty(N_CYCLES)
    f_inst_arr      = np.empty(N_CYCLES)
    Vtune_arr       = np.empty(N_CYCLES)
    vC1_arr         = np.empty(N_CYCLES)
    phi_err_raw_arr = np.empty(N_CYCLES)
    phi_err_pfd_arr = np.empty(N_CYCLES)
    t_pulse_arr     = np.empty(N_CYCLES)
    cycle_slip_times = []

    # "VCO first" ordering: VCO runs → reference edge arrives → PFD fires next cycle.
    # Initial t_pulse = 0 (no info yet), state = all zeros.
    state          = np.array([0.0, 0.0, 0.0])  # [phi_vco, Vtune, vC1]
    phi_ref_accum  = 0.0
    t_pulse        = 0.0
    Icp_signed     = 0.0   # no pulse before first REF edge
    prev_slip_floor = None

    for n in range(N_CYCLES):
        # 1. Log snapshot: state at start of cycle n, t_pulse to be applied this cycle
        t_arr[n]        = n * T_REF * 1e6                         # µs
        f_inst_arr[n]   = (F_FREE + KVCO * state[1]) / 1e9       # GHz
        Vtune_arr[n]    = state[1] * 1e3                          # mV
        vC1_arr[n]      = state[2] * 1e3                          # mV
        t_pulse_arr[n]  = t_pulse * 1e9                           # ns

        # 2. VCO runs for T_ref with current CP pulse
        state = sim_one_cycle(state, t_pulse, Icp_signed, T_REF)

        # 3. Reference edge arrives: accumulate one ref cycle
        phi_ref_accum += TWO_PI

        # 4. Compute phase error from phi_vco AFTER this cycle
        phi_fb         = state[0] / N
        phi_err_raw    = phi_ref_accum - phi_fb

        # 5. PFD: decide CP for NEXT cycle
        t_pulse, Icp_signed, phi_err_pfd = pfd(phi_err_raw)

        # 6. Cycle slip detection
        current_floor = int(np.floor(phi_err_raw / TWO_PI))
        if prev_slip_floor is None:
            prev_slip_floor = current_floor
        elif current_floor != prev_slip_floor:
            cycle_slip_times.append(n * T_REF * 1e6)
            prev_slip_floor = current_floor

        # 7. Log phase error (computed after ODE, before next cycle)
        phi_err_raw_arr[n] = phi_err_raw / TWO_PI   # cycles
        phi_err_pfd_arr[n] = phi_err_pfd             # rad

    return {
        't':               t_arr,
        'f_inst':          f_inst_arr,
        'Vtune':           Vtune_arr,
        'vC1':             vC1_arr,
        'phi_err_raw':     phi_err_raw_arr,
        'phi_err_pfd':     phi_err_pfd_arr,
        't_pulse':         t_pulse_arr,
        'cycle_slip_times': cycle_slip_times,
        'Vtune_lock':      (F_OUT - F_FREE) / KVCO * 1e3,  # mV
        'T_ref_ns':        T_REF * 1e9,
    }


if __name__ == '__main__':
    print(f"PLL transient sim: {N_CYCLES} cycles, F_FREE={F_FREE/1e9:.3f} GHz, "
          f"F_OUT={F_OUT/1e9:.3f} GHz, df={abs(F_OUT-F_FREE)/1e6:.0f} MHz")

    t0 = walltime.time()
    data = run()
    elapsed = walltime.time() - t0

    print(f"Done in {elapsed:.1f}s.")
    print(f"Cycle slips: {len(data['cycle_slip_times'])} "
          f"at t = {[f'{x:.1f}' for x in data['cycle_slip_times']]} us")
    print(f"Final: f_inst={data['f_inst'][-1]:.5f} GHz  "
          f"Vtune={data['Vtune'][-1]:.2f} mV  (target {data['Vtune_lock']:.1f} mV)")

    import plot
    plot.make_plots(data)
