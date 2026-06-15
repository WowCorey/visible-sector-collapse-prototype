"""Real-data smoke-test contact layer.

This module is a minimal, honest real-data contact layer. It can inspect a
lawful public CMB/FITS/HEALPix-style file that the user has explicitly provided
or downloaded, verify a SHA-256 checksum, read basic file metadata, and
optionally inspect FITS headers or HEALPix map metadata when the optional
dependencies (``astropy`` / ``healpy``) are installed.

It deliberately does **not** perform any cosmological inference. There is no
Planck likelihood, no topology covariance fit, no CLASS/CAMB transfer run, no
COMPACT eigenmode calculation, no model comparison, and no detection or
observational constraint. Passing this smoke test means only that a file was
located, checksummed, and inspected for basic metadata.

The optional inspectors import ``astropy`` / ``healpy`` lazily, so importing
this module never requires those packages.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .manifests import sha256_file

__all__ = [
    "SCOPE",
    "NO_CLAIMS",
    "sha256_file",
    "looks_like_fits",
    "basic_file_metadata",
    "inspect_fits_headers",
    "inspect_healpix_map",
    "build_smoke_manifest",
    "smoke_test_failures",
]

#: One-line scope statement embedded in every smoke-test manifest.
SCOPE = "real-data smoke test only; no observational inference"

#: Explicit list of claims this smoke test does *not* make.
NO_CLAIMS = [
    "no Planck likelihood",
    "no model validation",
    "no topology covariance fit",
    "no observational constraint",
    "no detection claim",
]

# Suffixes that suggest a FITS file. ``.fits.gz`` is handled via ``Path.suffixes``.
_FITS_SUFFIXES = {".fits", ".fit", ".fts"}


def looks_like_fits(path: str | Path) -> bool:
    """Return True if the path's suffixes suggest a FITS file (incl. ``.fits.gz``)."""
    suffixes = {suffix.lower() for suffix in Path(path).suffixes}
    return bool(suffixes & _FITS_SUFFIXES)


def basic_file_metadata(path: str | Path) -> dict[str, Any]:
    """Return file size, suffixes, and basic path metadata for a local file."""
    file_path = Path(path)
    stat = file_path.stat()  # raises FileNotFoundError for a missing file
    return {
        "name": file_path.name,
        "absolute_path": str(file_path.resolve()),
        "size_bytes": int(stat.st_size),
        "suffix": file_path.suffix,
        "suffixes": file_path.suffixes,
        "is_file": file_path.is_file(),
    }


def inspect_fits_headers(path: str | Path) -> dict[str, Any]:
    """Inspect FITS headers if ``astropy`` is installed.

    Raises a clear ``ImportError`` if ``astropy`` is missing. Does not fail the
    whole smoke test if the file is simply not a readable FITS file: in that
    case it returns ``{"status": "unreadable", ...}``. No cosmological
    computation is performed; only header metadata is summarised.
    """
    try:
        from astropy.io import fits
    except ImportError as exc:  # pragma: no cover - exercised when astropy absent
        raise ImportError(
            "FITS header inspection requires astropy. Install it with "
            "`pip install -e \".[fits]\"` or `pip install -e \".[realdata]\"`."
        ) from exc

    file_path = Path(path)
    try:
        with fits.open(file_path) as hdul:
            hdus = []
            for index, hdu in enumerate(hdul):
                header = hdu.header
                hdus.append(
                    {
                        "index": index,
                        "name": str(hdu.name),
                        "type": type(hdu).__name__,
                        "n_cards": len(header),
                        "naxis": int(header.get("NAXIS", 0)),
                        "bitpix": header.get("BITPIX"),
                        "keys": [str(key) for key in list(header.keys())[:50]],
                    }
                )
        return {"status": "ok", "n_hdus": len(hdus), "hdus": hdus}
    except Exception as exc:  # noqa: BLE001 - report, do not crash the smoke test
        return {"status": "unreadable", "reason": f"{type(exc).__name__}: {exc}"}


def inspect_healpix_map(path: str | Path) -> dict[str, Any]:
    """Inspect HEALPix map metadata if ``healpy`` is installed.

    Raises a clear ``ImportError`` if ``healpy`` is missing. Reports only safe
    metadata (nside, npix, number of maps, dtype, finite fraction). It does not
    compute any cosmological likelihood. If the file cannot be read as a HEALPix
    map it returns ``{"status": "unreadable", ...}``.
    """
    try:
        import healpy as hp
        import numpy as np
    except ImportError as exc:  # pragma: no cover - exercised when healpy absent
        raise ImportError(
            "HEALPix inspection requires healpy. Install it with "
            "`pip install -e \".[healpix]\"`."
        ) from exc

    file_path = Path(path)
    try:
        maps = hp.read_map(str(file_path), field=None)
        array = np.atleast_2d(maps)
        npix = int(array.shape[-1])
        return {
            "status": "ok",
            "nside": int(hp.npix2nside(npix)),
            "npix": npix,
            "n_maps": int(array.shape[0]),
            "dtype": str(np.asarray(maps).dtype),
            "finite_fraction": float(np.isfinite(array).mean()),
        }
    except Exception as exc:  # noqa: BLE001 - report, do not crash the smoke test
        return {"status": "unreadable", "reason": f"{type(exc).__name__}: {exc}"}


def _fits_status(path: Path, *, require_fits: bool) -> dict[str, Any]:
    if not looks_like_fits(path) and not require_fits:
        return {"status": "skipped", "reason": "file does not look like FITS"}
    try:
        result = inspect_fits_headers(path)
    except ImportError as exc:
        if require_fits:
            return {"status": "missing_dependency", "required": True, "reason": str(exc)}
        return {"status": "skipped_missing_astropy", "required": False, "reason": str(exc)}
    if require_fits:
        result = {**result, "required": True}
    return result


def _healpix_status(
    path: Path, *, try_healpix: bool, require_healpix: bool
) -> dict[str, Any]:
    if not (try_healpix or require_healpix):
        return {"status": "skipped", "reason": "HEALPix inspection not requested"}
    try:
        result = inspect_healpix_map(path)
    except ImportError as exc:
        if require_healpix:
            return {"status": "missing_dependency", "required": True, "reason": str(exc)}
        return {"status": "skipped_missing_healpy", "required": False, "reason": str(exc)}
    if require_healpix:
        result = {**result, "required": True}
    return result


def build_smoke_manifest(
    local_path: str | Path,
    *,
    source_name: str,
    input_kind: str,
    url: str | None = None,
    expected_sha256: str | None = None,
    require_fits: bool = False,
    try_healpix: bool = False,
    require_healpix: bool = False,
) -> dict[str, Any]:
    """Build a JSON-serializable smoke-test manifest with scope disclaimers.

    Computes the SHA-256 digest, compares it to ``expected_sha256`` when given,
    collects basic file metadata, and records optional FITS/HEALPix inspection
    statuses. It never raises on a checksum mismatch (the manifest records the
    mismatch via ``checksum_status``); callers decide the process exit code via
    :func:`smoke_test_failures`.
    """
    file_path = Path(local_path)
    if not file_path.exists():
        raise FileNotFoundError(f"input file does not exist: {file_path}")

    digest = sha256_file(file_path)
    if expected_sha256:
        normalized = expected_sha256.strip().lower()
        checksum_status = "pass" if digest.lower() == normalized else "fail"
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
        "local_path": str(file_path),
        "sha256": digest,
        "expected_sha256": normalized,
        "checksum_status": checksum_status,
        "file_metadata": basic_file_metadata(file_path),
        "fits_status": _fits_status(file_path, require_fits=require_fits),
        "healpix_status": _healpix_status(
            file_path, try_healpix=try_healpix, require_healpix=require_healpix
        ),
        "no_claims": list(NO_CLAIMS),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "tool": "viscollapse.realdata_smoke",
        "package_version": package_version,
    }


def smoke_test_failures(manifest: dict[str, Any]) -> list[str]:
    """Return human-readable reasons the smoke test should be treated as failed.

    A required inspection that did not succeed, or a checksum mismatch, are the
    only hard failures. Skipped optional inspections are not failures.
    """
    failures: list[str] = []

    if manifest.get("checksum_status") == "fail":
        failures.append(
            "checksum mismatch: expected "
            f"{manifest.get('expected_sha256')}, got {manifest.get('sha256')}"
        )

    fits = manifest.get("fits_status", {})
    if fits.get("required") and fits.get("status") != "ok":
        failures.append(f"required FITS inspection failed: {fits.get('status')}")

    healpix = manifest.get("healpix_status", {})
    if healpix.get("required") and healpix.get("status") != "ok":
        failures.append(
            f"required HEALPix inspection failed: {healpix.get('status')}"
        )

    return failures
