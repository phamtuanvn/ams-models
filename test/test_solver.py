from __future__ import annotations

import numpy as np
import pytest

from pll.config import F_FREE, T_REF, TWO_PI
from pll.solver import sim_one_cycle


class TestSolver:
    def test_free_running_phase(self):
        """With no CP pulse, VCO should advance by 2π·F_FREE·T_REF."""
        state = np.array([0.0, 0.0, 0.0])
        result = sim_one_cycle(state, 0.0, 0.0, T_REF)

        expected_phase = TWO_PI * F_FREE * T_REF
        assert result[0] == pytest.approx(expected_phase, rel=1e-6)

    def test_vtune_increases_with_up_current(self):
        state = np.array([0.0, 0.0, 0.0])
        result = sim_one_cycle(state, T_REF * 0.5, 130e-6, T_REF)
        assert result[1] > 0

    def test_vtune_decreases_with_down_current(self):
        state = np.array([0.0, 1.0, 1.0])
        result = sim_one_cycle(state, T_REF * 0.5, -130e-6, T_REF)
        assert result[1] < 1.0

    def test_state_shape(self):
        state = np.array([0.0, 0.0, 0.0])
        result = sim_one_cycle(state, 0.0, 0.0, T_REF)
        assert result.shape == (3,)
