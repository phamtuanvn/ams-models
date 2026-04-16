# ams-models

**Behavioral models for analog/mixed-signal IC blocks — for learning, simulation, and design verification.**

Mô hình behavioral cho các khối mạch analog/mixed-signal — phục vụ học tập, mô phỏng, và kiểm chứng thiết kế.

---

## Blocks / Các khối mạch

| Block | Status | Topology |
|-------|--------|----------|
| PLL   | 🚧 In progress | Integer-N, Charge Pump |
| LDO   | 📋 Planned | Linear regulator + feedback |
| ADC   | 📋 Planned | SAR |

---

## Approach / Phương pháp mô phỏng

- **PFD / CP / DIV:** Event-driven — triggered on rising edges
- **LPF / VCO:** Analytical update between events (no fixed timestep)
- **Validation:** Results cross-checked against linear transfer function (ζ, ωn, lock time)

This hybrid approach avoids fixed-timestep overhead while preserving accuracy for lock transient and phase noise analysis.

Cách tiếp cận hybrid này tránh được vấn đề timestep cố định, đồng thời vẫn đảm bảo độ chính xác cho phân tích lock transient và phase noise.

---

## Project structure / Cấu trúc thư mục

```
ams-models/
├── pll/                  # PLL behavioral model
│   ├── __init__.py
│   ├── pfd.py            # Phase-frequency detector
│   ├── cp.py             # Charge pump
│   ├── lpf.py            # Loop filter
│   ├── vco.py            # Voltage-controlled oscillator
│   └── divider.py        # Integer divider
├── ldo/                  # LDO behavioral model (planned)
├── notebooks/            # Jupyter demo notebooks
│   └── pll_demo.ipynb
├── tests/                # pytest test cases
│   └── test_pll.py
├── requirements.txt
└── README.md
```

---

## Getting started / Bắt đầu

**1. Clone and setup environment**

```bash
git clone https://github.com/YOUR_USERNAME/ams-models.git
cd ams-models

python -m venv .venv
source .venv/Scripts/activate      # Windows (Git Bash)
# source .venv/bin/activate        # Mac / Linux

pip install -r requirements.txt
```

**2. Run a PLL simulation**

```python
from pll import ChargePumpPLL

pll = ChargePumpPLL(
    f_ref=100e6,       # 100 MHz reference
    N=24,              # Divide ratio → 2.4 GHz output
    Kvco=200e6,        # 200 MHz/V
    Icp=100e-6,        # 100 µA charge pump
    R1=2e3, C1=100e-12, C2=10e-12
)

result = pll.simulate(t_end=20e-6)
result.plot()
```

**3. Run tests**

```bash
pytest tests/
```

---

## Requirements

```
numpy
scipy
matplotlib
jupyter
```

---

## Background / Bối cảnh

This repo is a companion to [AMS Blog](https://ams-blog.com) — a Vietnamese-language educational blog on analog/mixed-signal IC design.

Each model is built to be:
- **Readable:** Code structure mirrors circuit topology
- **Verifiable:** Key metrics (lock time, bandwidth, phase margin) cross-checked against hand calculations
- **Educational:** Notebooks explain the theory alongside the simulation

Repo này là tài liệu đi kèm với [AMS Blog](https://ams-blog.com) — kênh YouTube và blog tiếng Việt về thiết kế IC analog/mixed-signal.

Mỗi mô hình được xây dựng để:
- **Dễ đọc:** Cấu trúc code phản ánh topology mạch
- **Kiểm chứng được:** Các chỉ số quan trọng (lock time, bandwidth, phase margin) được đối chiếu với tính toán lý thuyết
- **Có giá trị học thuật:** Notebook giải thích lý thuyết song song với mô phỏng

---

## References / Tài liệu tham khảo

- B. Razavi, *Design of Analog CMOS Integrated Circuits*, 2nd ed.
- R. J. Baker, *CMOS Circuit Design, Layout, and Simulation*, 3rd ed.
- F. Gardner, "Charge-pump phase-lock loops," *IEEE Trans. Commun.*, 1980

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

> ⚠️ **Note:** This repo is under active development. APIs may change without notice.
>
> ⚠️ **Lưu ý:** Repo đang trong giai đoạn phát triển. API có thể thay đổi mà không báo trước.
