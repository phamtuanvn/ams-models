# ams-models

**Behavioral models for analog/mixed-signal IC blocks — for learning, simulation, and design verification.**

Mô hình behavioral cho các khối mạch analog/mixed-signal — phục vụ học tập, mô phỏng, và kiểm chứng thiết kế.

---

## Blocks / Các khối mạch

| Block | Status | Topology |
|-------|--------|----------|
| **PLL** | ✅ Working — lock transient | Integer-N charge-pump, type-II loop filter |
| LDO   | 📋 Planned | Linear regulator + feedback |
| ADC   | 📋 Planned | SAR |

→ PLL architecture, equations, and example plots: [`pll/README.md`](pll/README.md)

---

## Approach / Phương pháp mô phỏng

Event-driven, **no fixed global timestep**:

- **Per reference edge** — the PFD computes the wrapped phase error and the charge pump emits a current pulse (width ∝ error, polarity = up/down).
- **Between edges** — the loop-filter + VCO state `[φ_vco, V_tune, v_C1]` is integrated with an implicit solver (**Radau**), each reference period split into a CP-on and a CP-off phase. Implicit because the filter is stiff (`R·C1` and `R·C2` differ ~10×).
- **Validation** — large-signal results cross-checked against the small-signal 2nd-order loop (ζ, ωn, phase margin, lock time).

Cách tiếp cận event-driven này (không dùng timestep cố định toàn cục) giữ độ chính xác cho lock transient và cycle slip mà không phải dùng step nhỏ trên toàn bộ mô phỏng.

---

## Project structure / Cấu trúc thư mục

```
ams-models/
├── pll/                   # CP-PLL behavioral model  ✅
│   ├── README.md          # write-up: architecture, equations, figures
│   ├── config.py          # parameters + 2nd-order loop-dynamics sanity block
│   ├── pll_sim.py         # main driver — VCO-first loop, cycle-slip detection
│   ├── solver.py          # hybrid 2-phase-per-cycle ODE (Radau)
│   ├── plot.py            # 4-panel result plot
│   ├── components/        # pfd.py · vco.py · loop_filter.py
│   └── fig/               # block diagram + result plots
├── ldo/                   # LDO model (planned)
├── test/                  # tests (planned)
├── requirements.txt
└── README.md
```

---

## Getting started / Bắt đầu

```bash
git clone https://github.com/phamtuanvn/ams-models.git
cd ams-models

python -m venv .venv
source .venv/Scripts/activate      # Windows (Git Bash)
# source .venv/bin/activate        # macOS / Linux

pip install -r requirements.txt
```

**Run the PLL simulation** (edit `pll/config.py` to change parameters):

```bash
cd pll
python pll_sim.py
```

Prints the cycle-slip count and final lock state, and writes a 4-panel plot to `pll/output/`. Example (default config, Δf = 300 MHz):

```
Cycle slips: 5 at t = ['0.2', '0.4', '0.6', '1.3', '2.0'] us
Final: f_inst=2.39923 GHz  Vtune=1496.13 mV  (target 1500.0 mV)
```

---

## Requirements

```
numpy
scipy
matplotlib
```

---

## Background / Bối cảnh

This repo is a companion to [AMS Blog](https://ams-blog.com) — a Vietnamese-language educational blog on analog/mixed-signal IC design. Several articles walk through this exact PLL model.

Each model is built to be:
- **Readable:** code structure mirrors circuit topology
- **Verifiable:** key metrics (lock time, phase margin, ζ) cross-checked against hand calculations
- **Educational:** paired with a write-up that explains the theory alongside the simulation

Repo này đi kèm [AMS Blog](https://ams-blog.com) — blog tiếng Việt về thiết kế IC analog/mixed-signal. Một số bài trên blog dùng đúng model PLL trong repo này.

Mỗi mô hình được xây dựng để:
- **Dễ đọc:** cấu trúc code phản ánh topology mạch
- **Kiểm chứng được:** các chỉ số quan trọng (lock time, phase margin, ζ) đối chiếu với tính toán tay
- **Có giá trị học thuật:** đi kèm bài viết giải thích lý thuyết song song với mô phỏng

---

## References / Tài liệu tham khảo

- B. Razavi, *Design of Analog CMOS Integrated Circuits*, 2nd ed.
- R. J. Baker, *CMOS Circuit Design, Layout, and Simulation*, 3rd ed.
- F. Gardner, "Charge-pump phase-lock loops," *IEEE Trans. Commun.*, 1980

---

## License

MIT License — see [LICENSE](LICENSE).

---

> ⚠️ **Note:** under active development — structure and APIs may change without notice.
>
> ⚠️ **Lưu ý:** repo đang trong giai đoạn phát triển, cấu trúc/API có thể thay đổi mà không báo trước.
