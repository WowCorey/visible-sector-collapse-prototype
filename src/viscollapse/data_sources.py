"""Public source metadata for future real-data readiness work.

The manifest loaded here documents possible lawful public resources for future
work. It is not evidence that any real Planck/LAMBDA analysis has been run.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .manifests import load_yaml_manifest


REQUIRED_SOURCE_FIELDS = (
    "name",
    "type",
    "homepage",
    "data_access",
    "license_or_terms",
    "citation",
    "notes",
    "status",
)


def public_sources_path(repo_root: str | Path | None = None) -> Path:
    """Return the default public-source manifest path for a source checkout."""
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[2]
    return root / "data" / "public_sources.yml"


def load_public_sources(path: str | Path | None = None) -> dict[str, Any]:
    """Load and validate the public-source manifest."""
    manifest_path = Path(path) if path is not None else public_sources_path()
    manifest = load_yaml_manifest(manifest_path)
    validate_public_sources(manifest)
    return manifest


def validate_public_sources(manifest: dict[str, Any]) -> None:
    """Validate the minimal schema for ``data/public_sources.yml``."""
    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("public source manifest must contain a non-empty sources list")

    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            raise ValueError(f"source entry {index} must be a mapping")
        missing = [field for field in REQUIRED_SOURCE_FIELDS if field not in source]
        if missing:
            raise ValueError(f"source entry {index} is missing fields: {missing}")
