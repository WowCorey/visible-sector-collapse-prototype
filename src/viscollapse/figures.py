"""PNG figure generation for the synthetic prototype outputs.

This repository generates synthetic toy covariance matrices only. It does not
use real CMB data, Planck maps, CLASS/CAMB, COMPACT eigenmodes, masks, beams,
foreground models, or a Planck likelihood. It is a proof-of-method validation
of the mathematical machinery described in the associated discussion preprint.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .covariance import thermal_odd_block, toy_covariance_6x6
from .scans import scan_column_name

def plot_covariance_blocks(output_path: str | Path) -> None:
    """Write the zero visible thermal block and toy survivor block PNG."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    d6 = toy_covariance_6x6()
    max_abs = float(np.max(np.abs(d6)))

    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.2), constrained_layout=True)
    left = axes[0].imshow(
        thermal_odd_block(size=d6.shape[0]),
        cmap="RdBu_r",
        vmin=-max_abs,
        vmax=max_abs,
    )
    axes[0].set_title("Visible thermal odd block (zero)")
    axes[0].set_xlabel("toy index")
    axes[0].set_ylabel("toy index")
    fig.colorbar(left, ax=axes[0], fraction=0.046, pad=0.04)

    right = axes[1].imshow(d6, cmap="RdBu_r", vmin=-max_abs, vmax=max_abs)
    axes[1].set_title("Gravitational toy off-diagonal block")
    axes[1].set_xlabel("toy index")
    axes[1].set_ylabel("toy index")
    fig.colorbar(right, ax=axes[1], fraction=0.046, pad=0.04)

    fig.suptitle("Synthetic toy covariance blocks")
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

def plot_sn_scan(scan: pd.DataFrame, output_path: str | Path) -> None:
    """Write the analytic toy S/N scan PNG."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    for fpaired in (1.0, 0.5, 0.15):
        ax.plot(
            scan["lambda_b"],
            scan[scan_column_name(fpaired)],
            marker="o",
            label=f"f_phi={fpaired}",
        )
    ax.axhline(1.0, linestyle="--", linewidth=1, label="S/N=1")
    ax.set_xlabel("lambda_b")
    ax.set_ylabel("Toy S/N (q_SW=0.44)")
    ax.set_title("Analytic synthetic sensitivity scan")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

def plot_injected_recovered(mc117: pd.DataFrame, output_path: str | Path) -> None:
    """Write injected versus recovered amplitude for the 117-mode toy MC."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.errorbar(
        mc117["A_inj"],
        mc117["Ahat_mean"],
        yerr=mc117["Ahat_SE"],
        fmt="o",
        capsize=4,
        label="117-mode synthetic MC",
    )
    ax.plot([0, 1], [0, 1], linestyle="--", label="ideal recovery")
    ax.set_xlabel("Injected amplitude A_inj")
    ax.set_ylabel("Recovered mean Ahat")
    ax.set_title("Injected vs recovered amplitude (synthetic)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
