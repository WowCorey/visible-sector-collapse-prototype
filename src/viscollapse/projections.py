"""Visible-sector projection checks for the synthetic prototype.

This repository generates synthetic toy covariance matrices only. It does not
use real CMB data, Planck maps, CLASS/CAMB, COMPACT eigenmodes, masks, beams,
foreground models, or a Planck likelihood. It is a proof-of-method validation
of the mathematical machinery described in the associated discussion preprint.
"""

from __future__ import annotations

import numpy as np

def visible_projector() -> np.ndarray:
    """Return the 2x2 visible-sector projector ``P_vis``."""
    return np.array([[1.0, 0.0], [0.0, 0.0]], dtype=float)

def sector_swap() -> np.ndarray:
    """Return ``tau_1``, the visible-mirror sector-swap matrix."""
    return np.array([[0.0, 1.0], [1.0, 0.0]], dtype=float)

def visible_odd_projection() -> np.ndarray:
    """Return ``P_vis tau_1 P_vis``, which vanishes in the visible sector."""
    pvis = visible_projector()
    return pvis @ sector_swap() @ pvis

def visible_even_projection() -> np.ndarray:
    """Return ``P_vis I P_vis``, the nonzero even visible projection."""
    pvis = visible_projector()
    return pvis @ np.eye(2) @ pvis

def projection_check() -> dict[str, float]:
    """Return Frobenius norms for the odd and even projection checks."""
    odd = visible_odd_projection()
    even = visible_even_projection()
    return {
        "odd_projection_fro_norm": float(np.linalg.norm(odd, ord="fro")),
        "even_projection_fro_norm": float(np.linalg.norm(even, ord="fro")),
    }
