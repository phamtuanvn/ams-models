from __future__ import annotations

import time as walltime

import numpy as np

from .components.pfd import pfd
from .config import F_FREE, F_OUT, KVCO, N_CYCLES, T_REF, TWO_PI, N
from .solver import sim_one_cycle


def run() -> dict:
    t_arr           = np.empty(N_CYCLES)
    f_inst_arr      = np.empty(N_CYCLES)
    Vtune_arr       = np.empty(N_CYCLES)
    vC1_arr         = np.empty(N_CYCLES)
    phi_err_raw_arr = np.empty(N_CYCLES)
    phi_err_pfd_arr = np.empty(N_CYCLES)
    t_pulse_arr     = np.empty(N_CYCLES)
    cycle_slip_times: list[float] = []

    # "VCO first" ordering: VCO runs → reference edge arrives → PFD fires next cycle.
    state          = np.array([0.0, 0.0, 0.0])  # [phi_vco, Vtune, vC1]
    phi_ref_accum  = 0.0
    t_pulse        = 0.0
    Icp_signed     = 0.0
    prev_slip_floor: int | None = None

    for n in range(N_CYCLES):
        t_arr[n]        = n * T_REF * 1e6
        f_inst_arr[n]   = (F_FREE + KVCO * state[1]) / 1e9
        Vtune_arr[n]    = state[1] * 1e3
        vC1_arr[n]      = state[2] * 1e3
        t_pulse_arr[n]  = t_pulse * 1e9

        state = sim_one_cycle(state, t_pulse, Icp_signed, T_REF)

        phi_ref_accum += TWO_PI
        phi_fb         = state[0] / N
        phi_err_raw    = phi_ref_accum - phi_fb

        t_pulse, Icp_signed, phi_err_pfd = pfd(phi_err_raw)

        current_floor = int(np.floor(phi_err_raw / TWO_PI))
        if prev_slip_floor is None:
            prev_slip_floor = current_floor
        elif current_floor != prev_slip_floor:
            cycle_slip_times.append(n * T_REF * 1e6)
            prev_slip_floor = current_floor

        phi_err_raw_arr[n] = phi_err_raw / TWO_PI
        phi_err_pfd_arr[n] = phi_err_pfd

    return {
        't':               t_arr,
        'f_inst':          f_inst_arr,
        'Vtune':           Vtune_arr,
        'vC1':             vC1_arr,
        'phi_err_raw':     phi_err_raw_arr,
        'phi_err_pfd':     phi_err_pfd_arr,
        't_pulse':         t_pulse_arr,
        'cycle_slip_times': cycle_slip_times,
        'Vtune_lock':      (F_OUT - F_FREE) / KVCO * 1e3,
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

    from . import plot
    plot.make_plots(data)
