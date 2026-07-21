from __future__ import annotations

import numpy as np

F_REF    = 50e6       # Hz
F_OUT    = 2.4e9      # Hz
N        = 48
ICP_UP   = 130e-6     # A
ICP_DN   = 130e-6     # A
C1       = 15e-12     # F  (15 pF)
R        = 16e3       # Ω  (ζ ≈ 0.72)
C2       = 1.5e-12    # F  (1.5 pF)
KVCO     = 200e6      # Hz/V
F_FREE   = 2.1e9      # Hz  (Δf = 300 MHz → Vtune_lock = 1.5 V)
N_CYCLES = 100

T_REF  = 1.0 / F_REF    # 20 ns
TWO_PI = 2.0 * np.pi

# ── Loop dynamics (2nd-order approx, C1 >> C2) ──────────────────────────────
_wn  = np.sqrt(ICP_UP * KVCO / (N * C1))          # natural freq  (rad/s)
_wz  = 1 / (R * C1)                                # LF zero       (rad/s)
_wp2 = 1 / (R * C2)                                # LF pole       (rad/s)
_wc  = ICP_UP * KVCO * R / N                       # loop BW       (rad/s)
_PM  = np.degrees(np.arctan(_wc / _wz) - np.arctan(_wc / _wp2))   # deg
_zeta        = _wn * R * C1 / 2                    # 2nd-order closed-loop
_zeta_sanity = np.tan(np.radians(_PM)) / 2         # cross-check via PM
