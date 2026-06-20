# CP-PLL — Behavioral Transient Model

**Integer-N charge-pump PLL — large-signal transient model for lock acquisition, cycle slip, and settling analysis.**

Mô hình transient large-signal cho Integer-N charge-pump PLL — phân tích lock acquisition, cycle slip, và settling.

---

## What it does

Simulates the PLL **time-domain** behaviour that a linear (Bode / phase-margin) analysis cannot:

- Can the loop lock from a large initial frequency offset $\Delta f = f_{out} - f_{free}$?
- How long does lock take, and how many **cycle slips** happen first?
- How does settling / overshoot change with the loop-filter resistor $R$?

The model is **behavioral** — each block is a math equation, not a transistor netlist — but it captures the non-linear PFD wrap and large-signal pull-in correctly.

---

## Architecture

```
        ┌─────────┐   I_cp   ┌──────────────┐  V_tune  ┌─────┐ φ_vco
 ref ──▶│ PFD / CP │ ───────▶│ Loop filter  │ ───────▶│ VCO │ ──────┐
        └─────────┘          │ (R-C1 ∥ C2)  │          └─────┘       │
             ▲               └──────────────┘                        │
             │                       φ_vco / N                       │
             └──────────────────────── ÷N ◀──────────────────────────┘
```

| Block | Role | File |
|-------|------|------|
| **PFD + CP** | phase error → charge-pump current pulse (wrapped to ±π) | `components/pfd.py` |
| **Loop filter** | type-II, R–C1 in parallel with C2 | `components/loop_filter.py` |
| **VCO** | tune voltage → phase | `components/vco.py` |
| **Divider** | ÷N in the feedback path | inline in driver |

### Equations

State vector $\mathbf{y} = [\phi_{vco},\ V_{tune},\ v_{C1}]$.

**PFD + charge pump** — the PFD only sees the error wrapped into $(-\pi, \pi]$:

$$
\phi_{err,pfd} = \big[(\phi_{err,raw} + \pi)\ \mathrm{mod}\ 2\pi\big] - \pi
$$

$$
t_{pulse} = \min\!\left(\frac{|\phi_{err,pfd}|}{2\pi f_{ref}},\ T_{ref}\right),
\qquad
I_{CP} = \begin{cases} +I_{CP,up} & \phi_{err,pfd} \ge 0 \\ -I_{CP,dn} & \phi_{err,pfd} < 0 \end{cases}
$$

**Loop filter** (type-II):

$$
\frac{dV_{tune}}{dt} = \frac{I_{CP} - (V_{tune} - v_{C1})/R}{C_2},
\qquad
\frac{dv_{C1}}{dt} = \frac{V_{tune} - v_{C1}}{R\,C_1}
$$

**VCO** (voltage → frequency → phase):

$$
\frac{d\phi_{vco}}{dt} = 2\pi\left(f_{free} + K_{VCO}\,V_{tune}\right)
$$

---

## Numerical method — hybrid ODE

The charge pump only injects current for $t_{pulse}$ seconds after each reference edge, so every reference period $T_{ref}$ is split into **two phases**, solved sequentially:

- **Phase 1** $[0,\ t_{pulse}]$ — CP on  ($I_{CP} \neq 0$)
- **Phase 2** $[t_{pulse},\ T_{ref}]$ — CP off ($I_{CP} = 0$)

Each phase is integrated with **Radau** (implicit) because the filter has two very different time constants ($R\,C_2 = 75$ ns vs $R\,C_1 = 750$ ns) → stiff. Explicit solvers (RK45/DOP853) would crawl.

**"VCO-first" ordering:** within each cycle the VCO is advanced first, *then* the reference edge arrives and the phase error / PFD are evaluated — this avoids a spurious 1-cycle jump on the first iteration.

A **cycle slip** is detected when $\lfloor \phi_{err,raw} / 2\pi \rfloor$ changes between consecutive cycles.

---

## Files

```
pll/
├── config.py          # parameters + 2nd-order loop-dynamics sanity block (ωn, PM, ζ)
├── solver.py          # sim_one_cycle() — 2-phase-per-cycle hybrid ODE (Radau)
├── pll_sim.py         # main driver — VCO-first loop, cycle-slip detection
├── plot.py            # 4-panel result plot
└── components/
    ├── pfd.py         # PFD + charge pump
    ├── vco.py         # VCO phase rate
    └── loop_filter.py # type-II R-C1 ∥ C2 loop filter ODEs
```

---

## Default parameters (`config.py`)

| Param | Value | | Param | Value |
|---|---|---|---|---|
| `F_REF` | 50 MHz | | `C1` | 15 pF |
| `F_OUT` | 2.4 GHz | | `R` | 16 kΩ |
| `N` | 48 | | `C2` | 1.5 pF |
| `ICP_UP/DN` | 130 µA | | `F_FREE` | 2.1 GHz (Δf = 300 MHz) |
| `KVCO` | 200 MHz/V | | `N_CYCLES` | 100 (= 2 µs) |

Derived (printed by the loop-dynamics block in `config.py`): $\omega_n \approx 6.0$ Mrad/s, **$\zeta \approx 0.72$**, **PM $\approx 52.6°$**.

> $I_{CP}$ is deliberately small (130 µA) so cycle slips are clearly visible. With a larger $I_{CP}$ each CP pulse moves $V_{tune}$ enough to correct the phase error before it exceeds $2\pi$ — fewer slips.

---

## Run

```bash
pip install numpy scipy matplotlib
cd pll
python pll_sim.py
```

Prints the slip count + final state and writes a 4-panel plot to `output/`.

**Example (default config, Δf = 300 MHz):**

```
Cycle slips: 5 at t = ['0.2', '0.4', '0.6', '1.3', '2.0'] us
Final: f_inst=2.39923 GHz  Vtune=1496.13 mV  (target 1500.0 mV)
```

→ locks after **5 cycle slips** at ~2 µs.

---

## Validation

The large-signal model is cross-checked against the small-signal 2nd-order loop:

- $\zeta = \omega_n R C_1 / 2 \approx 0.721$, and $\tan(\mathrm{PM})/2$ from the exact open-loop phase margin agree to within the zero/$C_2$ approximation.
- Lock time, ringing frequency, and settling match the linear prediction once the loop is near lock.

---

## References

Full write-ups (in Vietnamese) on the AMS blog — these articles use this exact model:

- **CP-PLL Transient Simulation — Cycle Slip & Acquisition** (`/blog/pll-transient-sim-cycle-slip`) — builds the behavioral model, explains cycle slip, pull-in range.
- **CP-PLL Locking Transient — R vs Settling** (`/blog/pll-locking-transient`) — sweeps `R`, links phase margin ↔ time-domain settling.
- **PLL Loop Dynamics: Stability & Bandwidth** (`/blog/pll-loop-dynamics-stability-bandwidth`) — the linear / frequency-domain companion.
