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
from .data_sources import load_public_sources, public_sources_path
from .download import build_cache_path, download_file
from .manifests import sha256_file, verify_sha256
from .paper import build_paper_reproduction, validate_paper_reproduction
from .realdata_notes import readiness_scope
from .realdata_smoke import (
    basic_file_metadata,
    build_smoke_manifest,
    inspect_fits_headers,
    inspect_healpix_map,
    smoke_test_failures,
)
from .realmap_harmonics import (
    alm_table,
    build_realmap_manifest,
    cl_table_from_alms,
    extract_lowell_alms,
    read_healpix_temperature_map,
    require_healpy,
)

__version__ = "0.3.0"

__all__ = [
    "__version__",
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
    "load_public_sources",
    "public_sources_path",
    "build_cache_path",
    "download_file",
    "sha256_file",
    "verify_sha256",
    "build_paper_reproduction",
    "validate_paper_reproduction",
    "readiness_scope",
    "basic_file_metadata",
    "build_smoke_manifest",
    "inspect_fits_headers",
    "inspect_healpix_map",
    "smoke_test_failures",
    "require_healpy",
    "read_healpix_temperature_map",
    "extract_lowell_alms",
    "alm_table",
    "cl_table_from_alms",
    "build_realmap_manifest",
]
