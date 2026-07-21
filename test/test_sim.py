from __future__ import annotations

import numpy as np
import pytest

from pll.config import F_OUT, N_CYCLES
from pll.pll_sim import run


class TestSimulation:
    @pytest.fixture(scope="class")
    def sim_data(self):
        return run()

    def test_output_keys(self, sim_data):
        expected = {'t', 'f_inst', 'Vtune', 'vC1', 'phi_err_raw',
                    'phi_err_pfd', 't_pulse', 'cycle_slip_times',
                    'Vtune_lock', 'T_ref_ns'}
        assert set(sim_data.keys()) == expected

    def test_array_lengths(self, sim_data):
        for key in ['t', 'f_inst', 'Vtune', 'vC1', 'phi_err_raw',
                     'phi_err_pfd', 't_pulse']:
            assert len(sim_data[key]) == N_CYCLES

    def test_frequency_converges(self, sim_data):
        f_target = F_OUT / 1e9
        f_final = sim_data['f_inst'][-1]
        assert f_final == pytest.approx(f_target, rel=0.01)

    def test_no_nan(self, sim_data):
        for key in ['f_inst', 'Vtune', 'vC1']:
            assert not np.any(np.isnan(sim_data[key]))
