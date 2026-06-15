"""Real-map low-ell harmonic extraction (file-format + harmonic transform only).

This module is a minimal, honest real-map interface layer. Given a user-selected
lawful public HEALPix/FITS map, it can read one temperature-like map and extract
low-ell spherical-harmonic coefficients (a_lm) up to a chosen ``lmax`` using
``healpy.map2alm``. It can also produce a simple diagnostic C_l summary.

It deliberately performs **no cosmological inference**: no Planck likelihood, no
masks/noise/beam/foreground treatment, no topology covariance fit, no estimator
applied to real data, no CLASS/CAMB, no COMPACT eigenmodes, and no model
comparison. Extracting coefficients only proves the repository can read a map and
compute harmonic coefficients; it does not test the paper's cosmological model.

``healpy`` is an optional dependency and is imported lazily. The pure-Python
helpers (:func:`alm_table`, :func:`cl_table_from_alms`,
:func:`build_realmap_manifest`) do not require ``healpy``.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

__all__ = [
    "SCOPE",
    "NO_CLAIMS",
    "DEFAULT_EXTRACTION_SETTINGS",
    "require_healpy",
    "read_healpix_temperature_map",
    "extract_lowell_alms",
    "alm_table",
    "cl_table_from_alms",
    "build_realmap_manifest",
]

#: One-line scope statement embedded in every real-map manifest.
SCOPE = "real-map low-ell harmonic extraction only; no observational inference"

#: Explicit list of claims this extraction does *not* make.
NO_CLAIMS = [
    "no Planck likelihood",
    "no topology covariance fit",
    "no model comparison",
    "no estimator applied to real data",
    "no observational constraint",
    "no detection claim",
]

#: Boring, local-only extraction settings. ``use_pixel_weights`` is False so no
#: healpy weight files are ever downloaded.
DEFAULT_EXTRACTION_SETTINGS = {
    "pol": False,
    "iter": 0,
    "use_weights": False,
    "use_pixel_weights": False,
    "nest": False,
}


def require_healpy():
    """Return the ``healpy`` module, or raise a clear optional-dependency error."""
    try:
        import healpy as hp
    except ImportError as exc:
        raise ImportError(
            "healpy support is optional. Install with "
            '`python -m pip install -e ".[healpix]"`.'
        ) from exc
    return hp


def _validate_lmax(lmax: int) -> int:
    if isinstance(lmax, bool) or not isinstance(lmax, (int, np.integer)):
        raise ValueError(f"lmax must be an integer, got {lmax!r}")
    if lmax < 0:
        raise ValueError(f"lmax must be non-negative, got {lmax}")
    return int(lmax)


def _lm_arrays(lmax: int) -> tuple[np.ndarray, np.ndarray]:
    """Return (l, m) arrays in healpy's m-major alm storage order."""
    ells: list[int] = []
    ems: list[int] = []
    for m in range(lmax + 1):
        for ell in range(m, lmax + 1):
            ells.append(ell)
            ems.append(m)
    return np.asarray(ells, dtype=int), np.asarray(ems, dtype=int)


def read_healpix_temperature_map(
    path: str | Path, field: int = 0, nest: bool = False
) -> np.ndarray:
    """Read one temperature-like HEALPix map from FITS via ``healpy.read_map``.

    This is a file-format read only, not a cosmological analysis. The map is
    returned in RING ordering (``nest=False`` lets healpy convert if needed).
    """
    hp = require_healpy()
    return hp.read_map(str(path), field=field, nest=nest)


def extract_lowell_alms(map_array, lmax: int = 10) -> np.ndarray:
    """Extract low-ell ``a_lm`` values using ``healpy.map2alm``.

    Uses ``pol=False, iter=0, use_weights=False, use_pixel_weights=False`` so the
    transform is local-only and never triggers weight downloads.
    """
    _validate_lmax(lmax)
    hp = require_healpy()
    return hp.map2alm(
        map_array,
        lmax=lmax,
        pol=DEFAULT_EXTRACTION_SETTINGS["pol"],
        iter=DEFAULT_EXTRACTION_SETTINGS["iter"],
        use_weights=DEFAULT_EXTRACTION_SETTINGS["use_weights"],
        use_pixel_weights=DEFAULT_EXTRACTION_SETTINGS["use_pixel_weights"],
    )


def alm_table(alms, lmax: int) -> pd.DataFrame:
    """Return a DataFrame with columns l, m, alm_real, alm_imag, alm_abs."""
    _validate_lmax(lmax)
    values = np.asarray(alms, dtype=complex)
    ells, ems = _lm_arrays(lmax)
    if values.shape[0] != ells.shape[0]:
        raise ValueError(
            f"alm array length {values.shape[0]} does not match lmax={lmax} "
            f"(expected {ells.shape[0]})"
        )
    return pd.DataFrame(
        {
            "l": ells,
            "m": ems,
            "alm_real": values.real,
            "alm_imag": values.imag,
            "alm_abs": np.abs(values),
        }
    )


def cl_table_from_alms(alms, lmax: int) -> pd.DataFrame:
    """Return a simple diagnostic ``C_l`` summary from ``a_lm`` values.

    This is a diagnostic power summary only, not a likelihood or model
    comparison. ``C_l = (1/(2l+1)) * sum_m w_m |a_lm|^2`` with ``w_0 = 1`` and
    ``w_{m>0} = 2`` (matching ``healpy.alm2cl``).
    """
    _validate_lmax(lmax)
    values = np.asarray(alms, dtype=complex)
    ells, ems = _lm_arrays(lmax)
    if values.shape[0] != ells.shape[0]:
        raise ValueError(
            f"alm array length {values.shape[0]} does not match lmax={lmax} "
            f"(expected {ells.shape[0]})"
        )
    power = np.zeros(lmax + 1, dtype=float)
    weights = np.where(ems == 0, 1.0, 2.0)
    np.add.at(power, ells, weights * np.abs(values) ** 2)
    norm = 2 * np.arange(lmax + 1) + 1
    cl = power / norm
    return pd.DataFrame({"l": np.arange(lmax + 1), "cl": cl})


def build_realmap_manifest(
    *,
    source_name: str,
    input_kind: str,
    sha256: str,
    lmax: int,
    field: int,
    expected_sha256: str | None = None,
    url: str | None = None,
    local_path: str | Path | None = None,
    outputs: dict[str, Any] | None = None,
    settings: dict[str, Any] | None = None,
    ordering_assumption: str = "RING unless healpy converted otherwise",
) -> dict[str, Any]:
    """Return a JSON-serializable manifest with scope, source, checksum, options.

    ``sha256`` is supplied by the caller (computed once on the input file) so the
    file is not hashed twice. ``checksum_status`` is derived by comparing it to
    ``expected_sha256`` when provided.
    """
    if expected_sha256:
        normalized = expected_sha256.strip().lower()
        checksum_status = "pass" if sha256.lower() == normalized else "fail"
    else:
        normalized = None
        checksum_status = "not_provided"

    try:
        from . import __version__ as package_version
    except Exception:  # pragma: no cover - defensive only
        package_version = None

    return {
        "scope": SCOPE,
        "source_name": source_name,
        "input_kind": input_kind,
        "url": url,
        "local_path": str(local_path) if local_path is not None else None,
        "sha256": sha256,
        "expected_sha256": normalized,
        "checksum_status": checksum_status,
        "lmax": int(lmax),
        "field": int(field),
        "ordering_assumption": ordering_assumption,
        "settings": dict(settings) if settings else dict(DEFAULT_EXTRACTION_SETTINGS),
        "outputs": dict(outputs) if outputs else {},
        "no_claims": list(NO_CLAIMS),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "tool": "viscollapse.realmap_harmonics",
        "package_version": package_version,
    }
