"""No-internet unit tests for the real-data smoke-test contact layer.

These tests never download anything, never touch real Planck data, and do not
require astropy or healpy. When astropy is installed they additionally verify
FITS header reading using a tiny local FITS file created in ``tmp_path``.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from viscollapse.manifests import sha256_file
from viscollapse.realdata_smoke import (
    NO_CLAIMS,
    SCOPE,
    basic_file_metadata,
    build_smoke_manifest,
    inspect_fits_headers,
    looks_like_fits,
    smoke_test_failures,
)

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "realdata_smoke_test.py"


def _write_text_file(tmp_path: Path, name: str = "fake_public_file.txt") -> Path:
    path = tmp_path / name
    path.write_text("not real cmb data; smoke-test fixture only\n", encoding="utf-8")
    return path


def test_looks_like_fits_handles_gz_suffix():
    assert looks_like_fits("map.fits")
    assert looks_like_fits("map.fits.gz")
    assert looks_like_fits("map.fit")
    assert not looks_like_fits("notes.txt")


def test_basic_file_metadata_fields(tmp_path):
    source = _write_text_file(tmp_path)

    metadata = basic_file_metadata(source)

    assert metadata["name"] == "fake_public_file.txt"
    assert metadata["size_bytes"] > 0
    assert metadata["suffix"] == ".txt"
    assert metadata["is_file"] is True


def test_manifest_includes_scope_and_no_claims(tmp_path):
    source = _write_text_file(tmp_path)

    manifest = build_smoke_manifest(
        source,
        source_name="manual public source",
        input_kind="local_path",
    )

    assert manifest["scope"] == SCOPE
    assert "no observational inference" in manifest["scope"]
    assert manifest["no_claims"] == NO_CLAIMS
    assert manifest["source_name"] == "manual public source"
    assert manifest["input_kind"] == "local_path"
    assert manifest["checksum_status"] == "not_provided"
    assert manifest["fits_status"]["status"] == "skipped"
    assert manifest["healpix_status"]["status"] == "skipped"
    assert smoke_test_failures(manifest) == []


def test_checksum_pass(tmp_path):
    source = _write_text_file(tmp_path)
    expected = sha256_file(source)

    manifest = build_smoke_manifest(
        source,
        source_name="manual public source",
        input_kind="local_path",
        expected_sha256=expected,
    )

    assert manifest["checksum_status"] == "pass"
    assert manifest["sha256"] == expected
    assert smoke_test_failures(manifest) == []


def test_checksum_fail(tmp_path):
    source = _write_text_file(tmp_path)

    manifest = build_smoke_manifest(
        source,
        source_name="manual public source",
        input_kind="local_path",
        expected_sha256="0" * 64,
    )

    assert manifest["checksum_status"] == "fail"
    failures = smoke_test_failures(manifest)
    assert failures and "checksum mismatch" in failures[0]


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        build_smoke_manifest(
            tmp_path / "does_not_exist.fits",
            source_name="manual public source",
            input_kind="local_path",
        )


def test_require_fits_without_astropy_is_a_failure(tmp_path):
    """A non-FITS text file with --require-fits must surface a hard failure."""
    try:
        import astropy.io.fits  # noqa: F401

        has_astropy = True
    except ImportError:
        has_astropy = False

    source = _write_text_file(tmp_path)
    manifest = build_smoke_manifest(
        source,
        source_name="manual public source",
        input_kind="local_path",
        require_fits=True,
    )

    fits_status = manifest["fits_status"]
    assert fits_status["required"] is True
    if has_astropy:
        # astropy present but the text file is not valid FITS -> unreadable
        assert fits_status["status"] == "unreadable"
    else:
        assert fits_status["status"] == "missing_dependency"
    assert smoke_test_failures(manifest)


def test_inspect_fits_headers_behaviour(tmp_path):
    """If astropy is installed, read a tiny FITS file; otherwise expect ImportError."""
    try:
        from astropy.io import fits
        import numpy as np
    except ImportError:
        with pytest.raises(ImportError, match="astropy"):
            inspect_fits_headers(tmp_path / "anything.fits")
        return

    fits_path = tmp_path / "tiny.fits"
    hdu = fits.PrimaryHDU(np.zeros((2, 2), dtype="float32"))
    hdu.header["TELESCOP"] = "SMOKE-TEST"
    hdu.writeto(fits_path)

    result = inspect_fits_headers(fits_path)
    assert result["status"] == "ok"
    assert result["n_hdus"] >= 1
    assert result["hdus"][0]["naxis"] == 2

    manifest = build_smoke_manifest(
        fits_path,
        source_name="local synthetic fits fixture",
        input_kind="local_path",
        require_fits=True,
    )
    assert manifest["fits_status"]["status"] == "ok"
    assert smoke_test_failures(manifest) == []


# --- CLI exit-code tests (no network; --input only) ---------------------------


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def test_cli_help_exits_zero():
    result = _run_cli("--help")
    assert result.returncode == 0
    assert "smoke test" in result.stdout.lower()


def test_cli_local_file_success(tmp_path):
    source = _write_text_file(tmp_path)
    output = tmp_path / "smoke_manifest.json"

    result = _run_cli(
        "--input",
        str(source),
        "--source-name",
        "manual public source",
        "--output",
        str(output),
    )

    assert result.returncode == 0, result.stderr
    assert output.exists()
    manifest = json.loads(output.read_text(encoding="utf-8"))
    assert manifest["scope"] == SCOPE
    assert manifest["input_kind"] == "local_path"


def test_cli_checksum_mismatch_exits_nonzero(tmp_path):
    source = _write_text_file(tmp_path)

    result = _run_cli(
        "--input",
        str(source),
        "--source-name",
        "manual public source",
        "--expected-sha256",
        "0" * 64,
    )

    assert result.returncode == 1
    assert "checksum mismatch" in result.stderr.lower()


def test_cli_missing_file_exits_nonzero(tmp_path):
    result = _run_cli(
        "--input",
        str(tmp_path / "missing.fits"),
        "--source-name",
        "manual public source",
    )

    assert result.returncode == 1
    assert "error" in result.stderr.lower()
