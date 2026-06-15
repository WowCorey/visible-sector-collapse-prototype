# Real-data smoke test

This document describes the optional real-data smoke test added in the
real-data contact layer. It is intentionally minimal, conservative, and
reviewer-safe.

## What this does

- Verifies that a local or explicitly provided public CMB/FITS/HEALPix-style
  file can be accessed.
- Records basic file metadata (size, suffixes) and a SHA-256 checksum.
- Optionally reads FITS headers if `astropy` is installed.
- Optionally reads HEALPix map metadata (nside, npix, dtype, finite fraction)
  if `healpy` is installed.
- Writes a smoke-test manifest documenting source, checksum, file metadata, and
  scope.

## What this does NOT do

- No Planck likelihood.
- No topology covariance fit.
- No covariance analysis.
- No observational inference.
- No detection.
- No validation of the paper model.
- No CLASS/CAMB transfer run and no COMPACT eigenmode calculation.

The file is never fed into the topology estimator and is never compared against
the synthetic model.

> **Passing the real-data smoke test means only that a public file was accessed,
> checksummed, and inspected. It does not mean the theory was tested against
> Planck data.**

## Optional dependencies

The smoke test runs with the base install for local non-FITS files. FITS and
HEALPix inspection require optional extras and are never required in CI:

```bash
python -m pip install -e ".[fits]"      # astropy, FITS header inspection
python -m pip install -e ".[healpix]"   # healpy, HEALPix metadata
python -m pip install -e ".[realdata]"  # requests + PyYAML + astropy
```

If an optional dependency is missing, the smoke test skips that inspection and
records a clear status, unless you explicitly require it with `--require-fits`
or `--require-healpix`.

## Example local use

```bash
python -m pip install -e ".[realdata]"
python scripts/realdata_smoke_test.py \
  --input data/raw/YOUR_PUBLIC_FILE.fits \
  --source-name "Manually downloaded public Planck/LAMBDA file" \
  --expected-sha256 YOUR_SHA256 \
  --output results/realdata_smoke/smoke_manifest.json \
  --require-fits
```

## Example URL use

There is **no default URL**. You must explicitly pass `--url`, and downloads
never happen in CI. Verify the source's usage terms, version, checksum, and
citation requirements first.

```bash
python scripts/realdata_smoke_test.py \
  --url "PUBLIC_FILE_URL_CHOSEN_BY_USER" \
  --source-name "Explicit public source selected by user" \
  --expected-sha256 YOUR_SHA256 \
  --cache-dir data/cache \
  --output results/realdata_smoke/smoke_manifest.json
```

## Flags

| Flag | Meaning |
| --- | --- |
| `--input` | Path to an existing local public file. |
| `--url` | Explicit URL to download (mutually exclusive with `--input`). |
| `--source-name` | Required human-readable provenance label. |
| `--expected-sha256` | Optional expected digest; a mismatch fails the test. |
| `--cache-dir` | Cache directory for `--url` downloads (default `data/cache`). |
| `--output` | Optional manifest output path (also printed to stdout). |
| `--require-fits` | Fail if astropy is missing or the file is not readable FITS. |
| `--try-healpix` | Inspect HEALPix metadata if healpy is installed; skip otherwise. |
| `--require-healpix` | Fail if healpy is missing or the map is unreadable. |

## Exit codes

- `0` — file accessed and metadata inspection succeeded.
- non-zero — checksum mismatch, missing file, failed download, invalid
  arguments, or a *required* inspection (`--require-fits` / `--require-healpix`)
  that could not be satisfied.

## Manifest contents

The manifest is JSON and always includes the scope statement and an explicit
`no_claims` list, for example:

```json
{
  "scope": "real-data smoke test only; no observational inference",
  "source_name": "...",
  "input_kind": "local_path",
  "local_path": "...",
  "sha256": "...",
  "expected_sha256": null,
  "checksum_status": "not_provided",
  "file_metadata": {},
  "fits_status": {},
  "healpix_status": {},
  "no_claims": [
    "no Planck likelihood",
    "no model validation",
    "no topology covariance fit",
    "no observational constraint",
    "no detection claim"
  ]
}
```

Smoke-test manifests written under `results/realdata_smoke/` are git-ignored by
default (only `.gitkeep` is tracked). Copy a manifest into `docs/` deliberately
if you want to keep a record.

## Relationship to the synthetic reproduction

This smoke test is completely separate from the synthetic paper reproduction.
The synthetic Section 11 outputs are still produced only by:

```bash
python scripts/run_prototype.py
```

That command does not touch real data, and this smoke test does not touch the
synthetic model.
