"""Analytic lambda_b--f_phi_paired sensitivity scan.

This repository generates synthetic toy covariance matrices only. It does not
use real CMB data, Planck maps, CLASS/CAMB, COMPACT eigenmodes, masks, beams,
foreground models, or a Planck likelihood. It is a proof-of-method validation
of the mathematical machinery described in the associated discussion preprint.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from .constants import LAMBDA_B_VALUES, Q_SW_DEFAULT, FPAIRED_VALUES, N_MODES
from .utils import alpha_deg, a_topo, sw_ceiling, n_ring, f_ring

def lambda_fpaired_scan(
    lambda_values: Sequence[float] = LAMBDA_B_VALUES,
    fpaired_values: Sequence[float] = FPAIRED_VALUES,
    q_sw: float = Q_SW_DEFAULT,
    n_modes: int = N_MODES,
) -> pd.DataFrame:
    """Return the synthetic analytic S/N scan over lambda_b and f_phi_paired."""
    rows = []
    for lam in np.asarray(lambda_values, dtype=float):
        base_ceiling = float(sw_ceiling(lam, fpaired=1.0, f_sw=1.0, n_modes=n_modes))
        row = {
            "lambda_b": float(lam),
            "alpha_deg": float(alpha_deg(lam)),
            "A_topo": float(a_topo(lam)),
            "SW_ceiling_fpaired_1_fSW_1": base_ceiling,
            "N_ring": float(n_ring(lam)),
            "f_ring": float(f_ring(lam, n_modes=n_modes)),
        }
        for fp in fpaired_values:
            key = scan_column_name(float(fp), q_sw=q_sw)
            row[key] = base_ceiling * row["f_ring"] * q_sw * fp
        rows.append(row)
    return pd.DataFrame(rows)

def scan_column_name(fpaired: float, q_sw: float = Q_SW_DEFAULT) -> str:
    """Return the stable output column name for one synthetic scan curve."""
    q_label = f"{q_sw:.2f}".replace(".", "")
    fp_label = str(fpaired).replace(".", "_")
    return f"S_over_N_q{q_label}_fpaired_{fp_label}"
