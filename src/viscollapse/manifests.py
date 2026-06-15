"""Manifest and checksum helpers for real-data readiness.

These helpers support future lawful public-data integration. They do not fetch,
analyze, or validate real CMB data, and they do not run a Planck likelihood.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


class ChecksumMismatchError(ValueError):
    """Raised when a file digest does not match the expected SHA-256 value."""


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    """Return the SHA-256 hex digest for a local file."""
    file_path = Path(path)
    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_sha256(path: str | Path, expected_sha256: str) -> str:
    """Verify a local file against an expected SHA-256 digest."""
    if not expected_sha256:
        raise ValueError("expected_sha256 is required for checksum verification")

    actual = sha256_file(path)
    expected = expected_sha256.strip().lower()
    if actual.lower() != expected:
        raise ChecksumMismatchError(
            f"SHA-256 mismatch for {Path(path)}: expected {expected}, got {actual}"
        )
    return actual


def load_yaml_manifest(path: str | Path) -> dict[str, Any]:
    """Load a YAML manifest, requiring PyYAML only for manifest use."""
    try:
        import yaml
    except ImportError as exc:
        raise ImportError(
            "YAML manifest support is optional. Install with `pip install .[realdata]`."
        ) from exc

    manifest_path = Path(path)
    with manifest_path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    if not isinstance(loaded, dict):
        raise ValueError(f"Manifest {manifest_path} must contain a mapping")
    return loaded
