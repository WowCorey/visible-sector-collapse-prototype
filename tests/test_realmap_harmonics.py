"""No-internet unit tests for the real-map low-ell harmonic extraction layer.

These tests never download anything and never use real Planck data. They do not
require healpy: the pure-Python table/manifest helpers are tested directly, the
missing-dependency path is asserted when healpy is absent, and a tiny synthetic
HEALPix map is generated locally only when healpy happens to be installed.
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from viscollapse.manifests import sha256_file
from viscollapse.realmap_harmonics import (
    NO_CLAIMS,
    SCOPE,
    alm_table,
    build_realmap_manifest,
    cl_table_from_alms,
    extract_lowell_alms,
    require_healpy,
)

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "extract_lowell_alms.py"

try:
    import healpy as _hp  # noqa: F401

    HAS_HEALPY = True
except ImportError:
    HAS_HEALPY = False


def _alm_count(lmax: int) -> int:
    return (lmax + 1) * (lmax + 2) // 2


def _write_text_file(tmp_path: Path) -> Path:
    path = tmp_path / "fake_public_map.txt"
    path.write_text("not a real cmb map; fixture only\n", encoding="utf-8")
    return path


# --- pure-Python helpers (no healpy required) --------------------------------


def test_alm_table_columns_and_length():
    lmax = 3
    alms = np.arange(_alm_count(lmax), dtype=complex) + 1j
    table = alm_table(alms, lmax)

    assert list(table.columns) == ["l", "m", "alm_real", "alm_imag", "alm_abs"]
    assert len(table) == _alm_count(lmax)
    # healpy storage order is m-major: first lmax+1 entries are m=0.
    assert (table["m"].iloc[: lmax + 1] == 0).all()
    assert table["l"].max() == lmax


def test_cl_table_shape_and_monopole():
    lmax = 3
    alms = np.zeros(_alm_count(lmax), dtype=complex)
    alms[0] = 2.0  # (l=0, m=0)
    cl = cl_table_from_alms(alms, lmax)

    assert list(cl.columns) == ["l", "cl"]
    assert len(cl) == lmax + 1
    # C_0 = |a_00|^2 / 1 = 4.0
    assert cl.loc[cl["l"] == 0, "cl"].iloc[0] == pytest.approx(4.0)


def test_invalid_lmax_raises():
    with pytest.raises(ValueError, match="non-negative"):
        extract_lowell_alms(np.zeros(3), lmax=-1)
    with pytest.raises(ValueError, match="integer"):
        alm_table(np.zeros(3, dtype=complex), lmax=1.5)


def test_alm_table_length_mismatch_raises():
    with pytest.raises(ValueError, match="does not match lmax"):
        alm_table(np.zeros(5, dtype=complex), lmax=3)


# --- manifest -----------------------------------------------------------------


def test_manifest_scope_and_no_claims(tmp_path):
    source = _write_text_file(tmp_path)
    digest = sha256_file(source)

    manifest = build_realmap_manifest(
        source_name="manual public source",
        input_kind="local_path",
        sha256=digest,
        lmax=10,
        field=0,
        local_path=source,
    )

    assert manifest["scope"] == SCOPE
    assert "no observational inference" in manifest["scope"]
    assert manifest["no_claims"] == NO_CLAIMS
    assert manifest["lmax"] == 10
    assert manifest["field"] == 0
    assert manifest["ordering_assumption"].startswith("RING")
    assert manifest["settings"]["use_pixel_weights"] is False
    assert manifest["checksum_status"] == "not_provided"


def test_manifest_checksum_pass_and_fail(tmp_path):
    source = _write_text_file(tmp_path)
    digest = sha256_file(source)

    ok = build_realmap_manifest(
        source_name="s",
        input_kind="local_path",
        sha256=digest,
        lmax=4,
        field=0,
        expected_sha256=digest,
    )
    assert ok["checksum_status"] == "pass"

    bad = build_realmap_manifest(
        source_name="s",
        input_kind="local_path",
        sha256=digest,
        lmax=4,
        field=0,
        expected_sha256="0" * 64,
    )
    assert bad["checksum_status"] == "fail"


# --- optional-dependency behaviour -------------------------------------------


@pytest.mark.skipif(HAS_HEALPY, reason="healpy is installed")
def test_require_healpy_missing_raises():
    with pytest.raises(ImportError, match=r"healpix"):
        require_healpy()


@pytest.mark.skipif(HAS_HEALPY, reason="healpy is installed")
def test_cli_without_healpy_reports_missing_dependency(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--input",
            str(tmp_path / "whatever.fits"),
            "--source-name",
            "manual public source",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "healpy" in result.stderr.lower()


# --- end-to-end with healpy (synthetic local map only) ------------------------


@pytest.mark.skipif(not HAS_HEALPY, reason="healpy is not installed")
def test_extraction_on_tiny_synthetic_map(tmp_path):
    import healpy as hp

    nside = 2
    npix = hp.nside2npix(nside)
    sky_map = np.linspace(-1.0, 1.0, npix).astype(float)
    fits_path = tmp_path / "tiny_map.fits"
    hp.write_map(str(fits_path), sky_map, overwrite=True)

    lmax = 3
    output_dir = tmp_path / "out"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--input",
            str(fits_path),
            "--source-name",
            "local synthetic map fixture",
            "--lmax",
            str(lmax),
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    alm_csv = output_dir / f"alms_lmax{lmax}.csv"
    cl_csv = output_dir / f"cl_lmax{lmax}.csv"
    manifest_json = output_dir / "realmap_lowell_manifest.json"
    assert alm_csv.exists() and cl_csv.exists() and manifest_json.exists()

    manifest = json.loads(manifest_json.read_text(encoding="utf-8"))
    assert manifest["scope"] == SCOPE
    assert manifest["no_claims"] == NO_CLAIMS
    assert manifest["lmax"] == lmax


def test_cli_help_exits_zero():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "harmonic" in result.stdout.lower()
