"""Bias-subtracted quadratic amplitude estimator for toy Gaussian draws.

This repository generates synthetic toy covariance matrices only. It does not
use real CMB data, Planck maps, CLASS/CAMB, COMPACT eigenmodes, masks, beams,
foreground models, or a Planck likelihood. It is a proof-of-method validation
of the mathematical machinery described in the associated discussion preprint.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np
import pandas as pd

def quadratic_amplitude_estimator(samples: np.ndarray, template: np.ndarray) -> np.ndarray:
    """Return ``Ahat`` for samples drawn from ``C = I + A Delta C``.

    The estimator assumes the null covariance ``C0 = I`` and subtracts the
    trace bias, so this is a toy sanity check rather than a CMB likelihood.
    """
    samples = np.asarray(samples, dtype=float)
    template = np.asarray(template, dtype=float)
    if samples.ndim != 2:
        raise ValueError("samples must be a 2D array with shape (n_draws, n_modes)")
    if template.ndim != 2 or template.shape[0] != template.shape[1]:
        raise ValueError("template must be a square 2D array")
    if samples.shape[1] != template.shape[0]:
        raise ValueError("sample dimension must match template shape")

    denom = float(np.trace(template @ template))
    if denom == 0:
        raise ValueError("Template has zero norm")
    trace_bias = float(np.trace(template))
    q = np.einsum("bi,ij,bj->b", samples, template, samples)
    return (q - trace_bias) / denom

def monte_carlo_recovery(
    template: np.ndarray,
    amplitudes: Sequence[float] = (0.0, 0.5, 1.0),
    n_draws: int = 50_000,
    seed: int = 20260616,
) -> pd.DataFrame:
    """Run deterministic synthetic Gaussian injected-amplitude recovery tests.

    The single random-number generator is advanced across amplitudes in order.
    This preserves the regression values reported in the README and script
    output while keeping the run exactly reproducible for a fixed seed.
    """
    template = np.asarray(template, dtype=float)
    if n_draws <= 1:
        raise ValueError("n_draws must be greater than 1")
    if template.ndim != 2 or template.shape[0] != template.shape[1]:
        raise ValueError("template must be a square 2D array")

    rng = np.random.default_rng(seed)
    identity = np.eye(template.shape[0])
    rows = []
    for amp in amplitudes:
        cov = identity + amp * template
        eig_min = float(np.linalg.eigvalsh(cov)[0])
        if eig_min <= 0:
            rows.append({
                "A_inj": amp,
                "min_eig_cov": eig_min,
                "Ahat_mean": math.nan,
                "Ahat_SE": math.nan,
                "Ahat_std": math.nan,
                "status": "covariance not positive definite",
            })
            continue
        chol = np.linalg.cholesky(cov)
        z = rng.standard_normal((n_draws, template.shape[0]))
        samples = z @ chol.T
        estimates = quadratic_amplitude_estimator(samples, template)
        rows.append({
            "A_inj": amp,
            "min_eig_cov": eig_min,
            "Ahat_mean": float(estimates.mean()),
            "Ahat_SE": float(estimates.std(ddof=1) / math.sqrt(n_draws)),
            "Ahat_std": float(estimates.std(ddof=1)),
            "status": "pass",
        })
    return pd.DataFrame(rows)
