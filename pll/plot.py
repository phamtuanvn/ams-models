from __future__ import annotations

import os

import matplotlib
import numpy as np

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from .config import F_OUT

BG       = '#ffffff'
SURFACE  = '#f8fafc'
BORDER   = '#cbd5e1'
TEXT     = '#1e293b'
MUTED    = '#64748b'
SLIP_CLR = '#ea580c'

FS_LABEL = 11
FS_TICK  = 10
FS_ANNOT = 9


def _style_ax(ax: plt.Axes) -> None:
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=TEXT, labelsize=FS_TICK)
    for spine in ax.spines.values():
        spine.set_color(BORDER)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    ax.grid(True, color=BORDER, lw=0.5, ls=':')


def _slip_lines(ax: plt.Axes, times: list[float]) -> None:
    for ts in times:
        ax.axvline(ts, color=SLIP_CLR, alpha=0.35, lw=0.7, ls='--')


def make_plots(data: dict) -> None:
    t          = data['t']
    slips      = data['cycle_slip_times']
    n_slips    = len(slips)
    Vtune_lock = data['Vtune_lock']
    T_ref_ns   = data['T_ref_ns']

    fig, axes = plt.subplots(4, 1, figsize=(13, 11), sharex=True)
    fig.patch.set_facecolor(BG)
    fig.subplots_adjust(hspace=0.10, left=0.09, right=0.97, top=0.93, bottom=0.07)

    # Panel 1: f_inst
    ax = axes[0]
    _style_ax(ax)
    ax.plot(t, data['f_inst'], color='#2563eb', lw=0.8,
            rasterized=True, label='$f_{inst}$')
    ax.axhline(F_OUT / 1e9, color='#16a34a', lw=1.2, ls='--', alpha=0.9)
    _slip_lines(ax, slips)
    ax.set_ylabel('Frequency (GHz)', fontsize=FS_LABEL)
    ax.text(0.01, 0.88, f'{n_slips} cycle slip{"s" if n_slips != 1 else ""}',
            transform=ax.transAxes, color=SLIP_CLR, fontsize=FS_ANNOT)
    ax.text(0.99, 0.88, f'$f_{{out}}$ = {F_OUT/1e9:.3f} GHz',
            transform=ax.transAxes, color='#16a34a', fontsize=FS_ANNOT, ha='right')
    ax.legend(loc='lower right', fontsize=FS_ANNOT, facecolor=BG,
              edgecolor=BORDER, labelcolor=TEXT)

    # Panel 2: Vtune
    ax = axes[1]
    _style_ax(ax)
    ax.plot(t, data['Vtune'], color='#db2777', lw=0.8,
            label='$V_{tune}$', rasterized=True)
    ax.axhline(Vtune_lock, color='#16a34a', lw=1.2, ls='--', alpha=0.9)
    _slip_lines(ax, slips)
    ax.set_ylabel('$V_{tune}$ (mV)', fontsize=FS_LABEL)
    ax.text(0.99, 0.88, f'$V_{{tune,lock}}$ = {Vtune_lock:.1f} mV',
            transform=ax.transAxes, color='#16a34a', fontsize=FS_ANNOT, ha='right')
    ax.legend(loc='upper left', fontsize=FS_ANNOT,
              facecolor=BG, edgecolor=BORDER, labelcolor=TEXT)

    # Panel 3: Phase error
    ax = axes[2]
    _style_ax(ax)
    ax.plot(t, data['phi_err_raw'], color='#d97706', lw=0.9,
            label=r'$\phi_{err,raw}$ (cycles)', rasterized=True)
    ax.axhline(0, color=BORDER, lw=0.6)
    ax.set_ylabel(r'$\phi_{err,raw}$ (cycles)', fontsize=FS_LABEL)

    ax2 = ax.twinx()
    ax2.plot(t, data['phi_err_pfd'], color='#64748b', lw=0.5, alpha=0.6,
             label=r'$\phi_{err,pfd}$ (rad)', rasterized=True)
    ax2.set_ylim(-np.pi * 1.3, np.pi * 1.3)
    ax2.set_ylabel(r'$\phi_{err,pfd}$ (rad)', fontsize=FS_ANNOT, color=MUTED)
    ax2.tick_params(colors=MUTED, labelsize=FS_TICK - 1)
    ax2.axhline( np.pi, color=BORDER, lw=0.4, ls=':')
    ax2.axhline(-np.pi, color=BORDER, lw=0.4, ls=':')
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(
        lambda x, _: {0: '0', np.pi: '+π', -np.pi: '−π',
                      np.pi/2: '+π/2', -np.pi/2: '−π/2'}.get(round(x, 6), '')))
    for spine in ax2.spines.values():
        spine.set_color(BORDER)

    for ts in slips:
        idx = np.searchsorted(t, ts)
        if idx < len(t):
            ax.scatter(t[idx], data['phi_err_raw'][idx],
                       color=SLIP_CLR, s=30, zorder=5, linewidths=0)
    _slip_lines(ax, slips)

    l1 = ax.get_lines()[0]
    l2 = ax2.get_lines()[0]
    ax.legend([l1, l2], [l1.get_label(), l2.get_label()], loc='upper right',
              fontsize=FS_ANNOT, facecolor=BG, edgecolor=BORDER, labelcolor=TEXT)

    # Panel 4: CP pulse width
    ax = axes[3]
    _style_ax(ax)
    ax.plot(t, data['t_pulse'], color='#16a34a', lw=0.8, rasterized=True)
    ax.axhline(T_ref_ns, color=SLIP_CLR, lw=1.2, ls='--', alpha=0.9)
    _slip_lines(ax, slips)
    ax.set_ylabel('$t_{pulse}$ (ns)', fontsize=FS_LABEL)
    ax.set_xlabel('Time (µs)', fontsize=FS_LABEL)
    ax.text(0.99, 0.88, f'$T_{{ref}}$ = {T_ref_ns:.0f} ns (saturation)',
            transform=ax.transAxes, color=SLIP_CLR, fontsize=FS_ANNOT, ha='right')

    for ax in axes:
        ax.set_xlim(0, t[-1])

    fig.suptitle('Type-II CP-PLL — Transient Simulation', color=TEXT,
                 fontsize=13, fontweight='600')

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'pll_transient.svg')
    plt.savefig(out_path, bbox_inches='tight', facecolor=BG)
    print(f"Saved → {out_path}")
