"""Explicit downloader/cache helper for future public-data work.

This module never downloads anything at import time. Users must explicitly call
``download_file`` after verifying that the URL, terms, citation requirements,
and expected checksum are appropriate for their intended research use.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

from .manifests import verify_sha256


DEFAULT_USER_AGENT = "visible-sector-collapse-prototype/real-data-readiness"


def default_cache_dir(repo_root: str | Path | None = None) -> Path:
    """Return the default local cache directory, ``data/cache``."""
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    return root / "data" / "cache"


def cache_filename_from_url(url: str) -> str:
    """Return the final path component from a URL for cache naming."""
    if not url or not url.strip():
        raise ValueError("url is required")

    parsed = urlparse(url)
    filename = Path(unquote(parsed.path)).name
    if not filename:
        raise ValueError(f"could not derive a cache filename from URL: {url!r}")
    return filename


def build_cache_path(url: str, cache_dir: str | Path | None = None) -> Path:
    """Build a destination path under ``data/cache`` or a custom cache dir."""
    target_dir = Path(cache_dir) if cache_dir is not None else default_cache_dir()
    return target_dir / cache_filename_from_url(url)


def download_file(
    url: str,
    dest: str | Path | None = None,
    *,
    expected_sha256: str | None = None,
    cache_dir: str | Path | None = None,
    overwrite: bool = False,
) -> Path:
    """Download one explicitly requested URL and optionally verify SHA-256.

    No tests or package imports call this function against the internet. It is
    intended for future user-managed public-data downloads only.
    """
    if not url or not url.strip():
        raise ValueError("url is required")

    destination = Path(dest) if dest is not None else build_cache_path(url, cache_dir)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists() and not overwrite:
        if expected_sha256 is not None:
            verify_sha256(destination, expected_sha256)
        return destination

    request = Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
    with urlopen(request) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output)

    if expected_sha256 is not None:
        verify_sha256(destination, expected_sha256)
    return destination
