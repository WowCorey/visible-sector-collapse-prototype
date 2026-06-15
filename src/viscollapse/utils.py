"""Analytic helper functions for the synthetic sensitivity scan.

This repository generates synthetic toy covariance matrices only. It does not
use real CMB data, Planck maps, CLASS/CAMB, COMPACT eigenmodes, masks, beams,
foreground models, or a Planck likelihood. It is a proof-of-method validation
of the mathematical machinery described in the associated discussion preprint.
"""

from __future__ import annotations

import math

import numpy as np

def mode_count(ell_min: int = 2, ell_max: int = 10) -> int:
    """Return the synthetic scalar mode count for inclusive multipoles."""
    if ell_min < 0 or ell_max < ell_min:
        raise ValueError("require 0 <= ell_min <= ell_max")
    return sum(2 * ell + 1 for ell in range(ell_min, ell_max + 1))

def alpha_deg(lambda_b: float | np.ndarray) -> float | np.ndarray:
    """Return the toy ``arccos(lambda_b)`` angle in degrees."""
    return np.degrees(np.arccos(lambda_b))

def a_topo(lambda_b: float | np.ndarray) -> float | np.ndarray:
    """Return the synthetic analytic topological amplitude factor."""
    return np.sqrt(1.0 - np.asarray(lambda_b, dtype=float) ** 2)

def sw_prefactor(n_modes: int = 117) -> float:
    """Return the synthetic Sachs-Wolfe prefactor ``sqrt(N_modes / 2)``."""
    if n_modes <= 0:
        raise ValueError("n_modes must be positive")
    return math.sqrt(n_modes / 2.0)

def sw_ceiling(
    lambda_b: float | np.ndarray,
    fpaired: float = 1.0,
    f_sw: float = 1.0,
    n_modes: int = 117,
) -> float | np.ndarray:
    """Return the analytic toy Sachs-Wolfe amplitude ceiling."""
    return sw_prefactor(n_modes) * a_topo(lambda_b) * fpaired * f_sw

def n_ring(lambda_b: float | np.ndarray, ell_max: int = 10) -> float | np.ndarray:
    """Return the toy effective ring mode count."""
    return 2.0 * ell_max * np.sin(np.arccos(lambda_b)) + 1.0

def f_ring(
    lambda_b: float | np.ndarray,
    n_modes: int = 117,
    ell_max: int = 10,
) -> float | np.ndarray:
    """Return the synthetic ring fraction factor."""
    return np.sqrt(n_ring(lambda_b, ell_max=ell_max) / n_modes)
