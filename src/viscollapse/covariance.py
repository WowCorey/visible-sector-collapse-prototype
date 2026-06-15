"""Synthetic toy covariance templates and algebraic summaries.

This repository generates synthetic toy covariance matrices only. It does not
use real CMB data, Planck maps, CLASS/CAMB, COMPACT eigenmodes, masks, beams,
foreground models, or a Planck likelihood. It is a proof-of-method validation
of the mathematical machinery described in the associated discussion preprint.
"""

from __future__ import annotations

import numpy as np

from .constants import N_MODES

def thermal_odd_block(size: int = 6) -> np.ndarray:
    """Return the synthetic visible thermal odd block, exactly zero here."""
    if size <= 0:
        raise ValueError("size must be positive")
    return np.zeros((size, size), dtype=float)

def toy_covariance_6x6() -> np.ndarray:
    """Return the 6x6 synthetic toy off-diagonal covariance template."""
    return np.array([
        [0.00, 0.20, 0.00, 0.00, 0.00, 0.10],
        [0.20, 0.00, 0.15, 0.00, 0.00, 0.00],
        [0.00, 0.15, 0.00, 0.10, 0.00, 0.00],
        [0.00, 0.00, 0.10, 0.00, 0.05, 0.00],
        [0.00, 0.00, 0.00, 0.05, 0.00, 0.08],
        [0.10, 0.00, 0.00, 0.00, 0.08, 0.00],
    ], dtype=float)

def template_117_mode(n_modes: int = N_MODES) -> np.ndarray:
    """Return a synthetic ring template normalized to ``F_A = 1``.

    For the default ``2 <= ell <= 10`` low-ell range, ``n_modes = 117``.
    The ring has symmetric nearest-neighbor off-diagonal entries with weight
    ``1 / sqrt(n_modes)``, giving ``Tr(Delta C^2) = 2`` and ``F_A = 1``.
    """
    if n_modes < 3:
        raise ValueError("n_modes must be at least 3")
    template = np.zeros((n_modes, n_modes), dtype=float)
    edge_weight = 1.0 / np.sqrt(n_modes)
    for i in range(n_modes):
        j = (i + 1) % n_modes
        template[i, j] = edge_weight
        template[j, i] = edge_weight
    return template

def fisher_information(template: np.ndarray, c0_inv: np.ndarray | None = None) -> float:
    """Return toy Fisher information for an amplitude multiplying ``template``."""
    _validate_square(template, name="template")
    if c0_inv is None:
        c0_inv = np.eye(template.shape[0])
    _validate_square(c0_inv, name="c0_inv")
    if c0_inv.shape != template.shape:
        raise ValueError("c0_inv must have the same shape as template")
    return float(0.5 * np.trace(c0_inv @ template @ c0_inv @ template))

def template_summary(template: np.ndarray) -> dict[str, float]:
    """Return synthetic trace, Fisher, sigma, and eigenvalue diagnostics."""
    _validate_square(template, name="template")
    tr = float(np.trace(template))
    tr2 = float(np.trace(template @ template))
    fisher = 0.5 * tr2
    sigma = fisher ** -0.5 if fisher > 0 else np.inf
    eig = np.linalg.eigvalsh(template)
    return {
        "trace": tr,
        "trace_square": tr2,
        "fisher": float(fisher),
        "sigma_A": float(sigma),
        "min_eigenvalue": float(eig[0]),
        "max_eigenvalue": float(eig[-1]),
    }

def _validate_square(matrix: np.ndarray, *, name: str) -> None:
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"{name} must be a square 2D array")
