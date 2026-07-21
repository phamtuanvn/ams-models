from __future__ import annotations

import numpy as np
import pytest

from pll.components.loop_filter import lf_derivatives
from pll.components.pfd import pfd
from pll.components.vco import vco_dphi_dt
from pll.config import (
    C2,
    F_FREE,
    ICP_DN,
    ICP_UP,
    KVCO,
    T_REF,
    TWO_PI,
)


class TestVCO:
    def test_free_running(self):
        rate = vco_dphi_dt(0.0)
        assert rate == pytest.approx(TWO_PI * F_FREE, rel=1e-12)

    def test_positive_vtune(self):
        rate = vco_dphi_dt(1.0)
        expected = TWO_PI * (F_FREE + KVCO * 1.0)
        assert rate == pytest.approx(expected, rel=1e-12)

    def test_monotonic(self):
        assert vco_dphi_dt(1.0) > vco_dphi_dt(0.0)


class TestLoopFilter:
    def test_zero_current_equilibrium(self):
        dVtune, dvC1 = lf_derivatives(1.0, 1.0, 0.0)
        assert dVtune == pytest.approx(0.0, abs=1e-15)
        assert dvC1 == pytest.approx(0.0, abs=1e-15)

    def test_positive_current(self):
        dVtune, dvC1 = lf_derivatives(0.0, 0.0, ICP_UP)
        assert dVtune == pytest.approx(ICP_UP / C2, rel=1e-12)
        assert dvC1 == pytest.approx(0.0, abs=1e-15)


class TestPFD:
    def test_zero_error(self):
        t_pulse, Icp, phi_pfd = pfd(0.0)
        assert t_pulse == pytest.approx(0.0, abs=1e-15)
        assert phi_pfd == pytest.approx(0.0, abs=1e-15)

    def test_positive_error_pumps_up(self):
        t_pulse, Icp, phi_pfd = pfd(0.5)
        assert Icp == pytest.approx(ICP_UP)
        assert t_pulse > 0

    def test_negative_error_pumps_down(self):
        t_pulse, Icp, phi_pfd = pfd(-0.5)
        assert Icp == pytest.approx(-ICP_DN)
        assert t_pulse > 0

    def test_pulse_clamped_to_tref(self):
        t_pulse, _, _ = pfd(100 * TWO_PI + np.pi * 0.99)
        assert t_pulse <= T_REF + 1e-15

    def test_wrapping(self):
        _, _, phi1 = pfd(0.1)
        _, _, phi2 = pfd(0.1 + TWO_PI)
        assert phi1 == pytest.approx(phi2, abs=1e-12)
