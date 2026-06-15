"""Real-data smoke test for an explicitly selected lawful public file.

This is a separate, honest real-data contact layer. It is NOT the synthetic
paper reproduction (`scripts/run_prototype.py`) and it does NOT perform a Planck
likelihood, topology covariance fit, CLASS/CAMB run, COMPACT eigenmode
calculation, model comparison, or any observational inference. It only checks
that a user-provided public CMB/FITS/HEALPix-style file can be located,
checksummed, and inspected for basic metadata, then writes a manifest.

The file is never fed into the topology estimator and is never compared against
the synthetic model.

Examples
--------
Local file::

    python scripts/realdata_smoke_test.py \\
        --input data/raw/YOUR_PUBLIC_FILE.fits \\
        --source-name "manual public source" \\
        --output results/realdata_smoke/smoke_manifest.json

Explicit URL (no default URL; never downloaded in CI)::

    python scripts/realdata_smoke_test.py \\
        --url "https://example-public-source/file.fits" \\
        --source-name "manual public source" \\
        --cache-dir data/cache \\
        --output results/realdata_smoke/smoke_manifest.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from viscollapse.download import download_file  # noqa: E402
from viscollapse.realdata_smoke import (  # noqa: E402
    SCOPE,
    build_smoke_manifest,
    smoke_test_failures,
)

URL_TERMS_WARNING = (
    "WARNING: You requested an explicit download. Verify the source's usage "
    "terms, version, checksum, and citation requirements before using this file."
)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="realdata_smoke_test.py",
        description=(
            "Real-data file-access and metadata smoke test. "
            f"Scope: {SCOPE}. No Planck likelihood, no model validation."
        ),
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", help="Path to an existing local public file.")
    source.add_argument(
        "--url",
        help="Explicit URL to download (no default; never used in CI).",
    )
    parser.add_argument(
        "--source-name",
        required=True,
        help="Human-readable provenance label, e.g. 'manual public source'.",
    )
    parser.add_argument(
        "--expected-sha256",
        default=None,
        help="Optional expected SHA-256 digest; a mismatch fails the smoke test.",
    )
    parser.add_argument(
        "--cache-dir",
        default=None,
        help="Cache directory for --url downloads (default: data/cache).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional path to write the manifest JSON (printed to stdout regardless).",
    )
    parser.add_argument(
        "--require-fits",
        action="store_true",
        help="Fail if astropy is missing or the file is not a readable FITS file.",
    )
    parser.add_argument(
        "--try-healpix",
        action="store_true",
        help="Inspect HEALPix metadata if healpy is installed; skip otherwise.",
    )
    parser.add_argument(
        "--require-healpix",
        action="store_true",
        help="Fail if healpy is missing or the file is not a readable HEALPix map.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the smoke test and return a process exit code."""
    args = _parse_args(argv)

    try:
        if args.url is not None:
            print(URL_TERMS_WARNING, file=sys.stderr)
            cache_dir = Path(args.cache_dir) if args.cache_dir else None
            # Download without an inline checksum so the manifest records the
            # comparison result instead of raising before a manifest is built.
            local_path = download_file(args.url, cache_dir=cache_dir)
            input_kind = "url"
        else:
            local_path = Path(args.input)
            input_kind = "local_path"

        manifest = build_smoke_manifest(
            local_path,
            source_name=args.source_name,
            input_kind=input_kind,
            url=args.url,
            expected_sha256=args.expected_sha256,
            require_fits=args.require_fits,
            try_healpix=args.try_healpix,
            require_healpix=args.require_healpix,
        )
    except FileNotFoundError as exc:
        print(f"Smoke test error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 - failed download / unexpected IO
        print(f"Smoke test error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    rendered = json.dumps(manifest, indent=2, sort_keys=True)
    print(rendered)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"Manifest written to {output_path}", file=sys.stderr)

    failures = smoke_test_failures(manifest)
    if failures:
        print("Smoke test failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(
        "Smoke test passed: file accessed, checksummed, and inspected. "
        "No observational inference was performed.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
