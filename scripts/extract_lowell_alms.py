"""Extract low-ell harmonic coefficients from a user-selected public map.

This is a separate, honest real-map interface. It is NOT the synthetic paper
reproduction (`scripts/run_prototype.py`) and it does NOT perform a Planck
likelihood, masks/noise/beam/foreground treatment, topology covariance fit,
estimator on real data, CLASS/CAMB run, COMPACT eigenmodes, or model comparison.

It reads one temperature-like HEALPix/FITS map that the user explicitly provided
or downloaded, extracts low-ell a_lm coefficients up to ``--lmax``, writes an
a_lm CSV, a simple C_l diagnostic CSV, and a no-claims manifest.

A successful extraction only proves the repository can read a selected map and
produce low-ell harmonic coefficients. It does not test the paper's model.

Examples
--------
Local map::

    python scripts/extract_lowell_alms.py \\
        --input data/raw/YOUR_PUBLIC_MAP.fits \\
        --source-name "manual public source" \\
        --lmax 10 --field 0 \\
        --output-dir results/realmap_lowell

Explicit URL (no default URL; never downloaded in CI)::

    python scripts/extract_lowell_alms.py \\
        --url "USER_SELECTED_PUBLIC_FILE_URL" \\
        --source-name "manual public source" \\
        --cache-dir data/cache --lmax 10 \\
        --output-dir results/realmap_lowell
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
from viscollapse.manifests import sha256_file  # noqa: E402
from viscollapse.realmap_harmonics import (  # noqa: E402
    DEFAULT_EXTRACTION_SETTINGS,
    SCOPE,
    alm_table,
    build_realmap_manifest,
    cl_table_from_alms,
    extract_lowell_alms,
    read_healpix_temperature_map,
    require_healpy,
)

URL_TERMS_WARNING = (
    "WARNING: You requested an explicit download. Verify the source's usage "
    "terms, version, checksum, and citation requirements before using this file."
)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="extract_lowell_alms.py",
        description=(
            "Real-map low-ell harmonic extraction. "
            f"Scope: {SCOPE}. No Planck likelihood, no model test."
        ),
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", help="Path to an existing local public map.")
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
        help="Optional expected SHA-256 digest; a mismatch fails the run.",
    )
    parser.add_argument(
        "--lmax", type=int, default=10, help="Maximum multipole (default: 10)."
    )
    parser.add_argument(
        "--field", type=int, default=0, help="HEALPix map field/column (default: 0)."
    )
    parser.add_argument(
        "--cache-dir",
        default=None,
        help="Cache directory for --url downloads (default: data/cache).",
    )
    parser.add_argument(
        "--output-dir",
        default="results/realmap_lowell",
        help="Directory for CSV/JSON outputs (default: results/realmap_lowell).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the extraction and return a process exit code."""
    args = _parse_args(argv)

    if args.lmax < 0:
        print(f"Error: --lmax must be non-negative, got {args.lmax}", file=sys.stderr)
        return 1

    # healpy is required for actual extraction; fail clearly and early.
    try:
        require_healpy()
    except ImportError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    try:
        if args.url is not None:
            print(URL_TERMS_WARNING, file=sys.stderr)
            cache_dir = Path(args.cache_dir) if args.cache_dir else None
            local_path = download_file(args.url, cache_dir=cache_dir)
            input_kind = "url"
        else:
            local_path = Path(args.input)
            input_kind = "local_path"
            if not local_path.exists():
                print(f"Error: input file does not exist: {local_path}", file=sys.stderr)
                return 1

        digest = sha256_file(local_path)
        if args.expected_sha256:
            expected = args.expected_sha256.strip().lower()
            if digest.lower() != expected:
                print(
                    f"Error: SHA-256 mismatch: expected {expected}, got {digest}",
                    file=sys.stderr,
                )
                return 1

        sky_map = read_healpix_temperature_map(local_path, field=args.field)
        alms = extract_lowell_alms(sky_map, lmax=args.lmax)
        alms_df = alm_table(alms, args.lmax)
        cl_df = cl_table_from_alms(alms, args.lmax)
    except Exception as exc:  # noqa: BLE001 - failed download / read / transform
        print(f"Extraction error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    alm_csv = output_dir / f"alms_lmax{args.lmax}.csv"
    cl_csv = output_dir / f"cl_lmax{args.lmax}.csv"
    manifest_json = output_dir / "realmap_lowell_manifest.json"

    alms_df.to_csv(alm_csv, index=False)
    cl_df.to_csv(cl_csv, index=False)

    manifest = build_realmap_manifest(
        source_name=args.source_name,
        input_kind=input_kind,
        sha256=digest,
        lmax=args.lmax,
        field=args.field,
        expected_sha256=args.expected_sha256,
        url=args.url,
        local_path=local_path,
        outputs={
            "alm_csv": str(alm_csv),
            "cl_csv": str(cl_csv),
            "manifest_json": str(manifest_json),
        },
        settings=DEFAULT_EXTRACTION_SETTINGS,
    )
    manifest_json.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(f"Extracted low-ell a_lm up to lmax={args.lmax} from {local_path}")
    print(f"  a_lm table:   {alm_csv}")
    print(f"  C_l summary:  {cl_csv}")
    print(f"  manifest:     {manifest_json}")
    print(
        "Harmonic extraction only: no Planck likelihood, no topology fit, "
        "no estimator on real data, no model comparison, no observational claim.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
