"""Shared constants for the synthetic covariance prototype.

This repository generates synthetic toy covariance matrices only. It does not
use real CMB data, Planck maps, CLASS/CAMB, COMPACT eigenmodes, masks, beams,
foreground models, or a Planck likelihood. It is a proof-of-method validation
of the mathematical machinery described in the associated discussion preprint.
"""

from __future__ import annotations

ELL_MIN = 2
ELL_MAX = 10
N_MODES = sum(2 * ell + 1 for ell in range(ELL_MIN, ELL_MAX + 1))

LAMBDA_B_VALUES = (0.55, 0.65, 0.75, 0.85, 0.95)
Q_SW_DEFAULT = 0.44
FPAIRED_VALUES = (1.0, 0.5, 0.15)

SEED_6X6 = 20260615
SEED_117 = 20260616
