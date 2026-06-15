# Real-map low-ell harmonic extraction

This document describes the optional real-map low-ell harmonic extraction
utility. It is intentionally minimal, conservative, and reviewer-safe.

## What this does

- Reads a user-provided public HEALPix/FITS map (one temperature-like field).
- Extracts low-ell spherical-harmonic coefficients (a_lm) up to a chosen `lmax`
  using `healpy.map2alm`.
- Writes `alms_lmax*.csv`, a simple `cl_lmax*.csv` diagnostic, and a no-claims
  manifest (`realmap_lowell_manifest.json`).

## What this does NOT do

- No Planck likelihood.
- No masks, noise, beam, or foreground treatment.
- No topology covariance fit.
- No estimator applied to real data.
- No model comparison.
- No CLASS/CAMB and no COMPACT eigenmodes.
- No observational inference, detection, or constraint.

The extracted coefficients are never fed into the topology estimator and are
never compared against the synthetic model.

> **A successful extraction only proves the repository can read a selected map
> and produce low-ell harmonic coefficients. It does not test the paper's
> cosmological model.**

## Optional dependency

Harmonic extraction requires `healpy`, which is optional and never required for
the base install or CI:

```bash
python -m pip install -e ".[healpix]"
```

If `healpy` is missing, the script fails clearly with:

```text
healpy support is optional. Install with `python -m pip install -e ".[healpix]"`.
```

The extraction is deliberately local-only and boring: `pol=False`, `iter=0`,
`use_weights=False`, and `use_pixel_weights=False`. Pixel weights are disabled so
the transform never triggers an automatic healpy weight download. These settings
are recorded in the manifest.

## Example local use

```bash
python -m pip install -e ".[healpix]"
python scripts/extract_lowell_alms.py \
  --input data/raw/YOUR_PUBLIC_MAP.fits \
  --source-name "Manually selected public CMB map" \
  --expected-sha256 YOUR_SHA256 \
  --lmax 10 \
  --field 0 \
  --output-dir results/realmap_lowell
```

## Example URL use

There is **no default URL**, and downloads never happen in CI. You must pass
`--url` explicitly and verify the source's usage terms, version, checksum, and
citation requirements first.

```bash
python scripts/extract_lowell_alms.py \
  --url "USER_SELECTED_PUBLIC_FILE_URL" \
  --source-name "Explicit public source selected by user" \
  --expected-sha256 YOUR_SHA256 \
  --cache-dir data/cache \
  --lmax 10 \
  --field 0 \
  --output-dir results/realmap_lowell
```

## Outputs

Written under `results/realmap_lowell/` (git-ignored by default, only `.gitkeep`
is tracked):

| File | Contents |
| --- | --- |
| `alms_lmax<L>.csv` | Columns `l, m, alm_real, alm_imag, alm_abs`. |
| `cl_lmax<L>.csv` | Columns `l, cl` (diagnostic power summary only). |
| `realmap_lowell_manifest.json` | Source, checksum, options, and `no_claims`. |

The manifest always includes
`"scope": "real-map low-ell harmonic extraction only; no observational inference"`
and the explicit `no_claims` list.

## Exit codes

- `0` — map read and coefficients extracted successfully.
- non-zero — missing `healpy`, missing input file, checksum mismatch, failed
  download, invalid `--lmax`, or an unreadable map.

## Relationship to the synthetic reproduction

This utility is completely separate from the synthetic paper reproduction. The
synthetic Section 11 outputs are still produced only by:

```bash
python scripts/run_prototype.py
```

That command does not touch real data, and this extraction does not touch the
synthetic model, `results/paper_v7/`, or `figures/paper_v7/`.
