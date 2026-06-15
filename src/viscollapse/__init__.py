"""Synthetic low-ell covariance prototype package.

This repository generates synthetic toy covariance matrices only. It does not
use real CMB data, Planck maps, CLASS/CAMB, COMPACT eigenmodes, masks, beams,
foreground models, or a Planck likelihood. It is a proof-of-method validation
of the mathematical machinery described in the associated discussion preprint.
"""

from .projections import (
    projection_check,
    sector_swap,
    visible_even_projection,
    visible_odd_projection,
    visible_projector,
)
from .covariance import (
    fisher_information,
    template_117_mode,
    template_summary,
    thermal_odd_block,
    toy_covariance_6x6,
)
from .estimator import quadratic_amplitude_estimator, monte_carlo_recovery
from .scans import lambda_fpaired_scan, scan_column_name

__all__ = [
    "visible_projector",
    "sector_swap",
    "visible_odd_projection",
    "visible_even_projection",
    "projection_check",
    "thermal_odd_block",
    "toy_covariance_6x6",
    "template_117_mode",
    "fisher_information",
    "template_summary",
    "quadratic_amplitude_estimator",
    "monte_carlo_recovery",
    "lambda_fpaired_scan",
    "scan_column_name",
]
