# Release Audit — v0.3.0 (Paper Reproducibility Companion)

**Date:** 2026-06-15
**Branch audited:** `main` (PRs #1, #2, #3 merged)
**Audit type:** Verification-only release audit (no rewrite)
**Package version:** `0.3.0`
**Paper:** *The Visible-Sector Collapse in Dressed Non-Orientable Cosmology* (v7.1), Corey Luisi

## Summary

A prior gap analysis claimed that the core modules, paper-reproduction script,
master notebook, tests, README, and committed outputs were missing. **That gap
analysis is stale and no longer accurate.** The current `main` branch already
satisfies all critical reproducibility requirements for linking the repository
from the paper as a **synthetic reproducibility companion**.

The repository remains **synthetic-only** for all implemented outputs. No real
CMB data, Planck maps, CLASS/CAMB execution, COMPACT eigenmodes, or
observational likelihoods are present. No changes to scientific results were
made by this audit.

## Commands run

| Command | Result |
| --- | --- |
| `python -m pip install -e ".[dev]"` | Success — editable install of `visible-sector-collapse-prototype-0.3.0` |
| `python -m pytest -q` | **20 passed** |
| `python scripts/run_prototype.py` | **Exit code 0**; all paper-value checks pass |
| `python -m compileall -q src scripts` | **Exit code 0** |
| Notebook JSON validation (all 5 `.ipynb`) | All valid (`nbformat` 4) |

## Checklist verification

### 1. Implemented core modules — PASS
- `src/viscollapse/projections.py` ✓
- `src/viscollapse/covariance.py` ✓
- `src/viscollapse/estimator.py` ✓
- `src/viscollapse/scans.py` ✓
- `src/viscollapse/paper.py` ✓

### 2. End-to-end script — PASS
- `scripts/run_prototype.py` ✓
- Runs all Section 11 synthetic checks ✓
- Saves outputs to `results/paper_v7/` and figures to `figures/paper_v7/` ✓
- Validates headline values via `validate_paper_reproduction()` and exits
  nonzero on failure (`main()` returns `1`; `raise SystemExit(main())`) ✓

### 3. Master notebook — PASS
- `notebooks/reproduce_paper_results.ipynb` (20 cells: 11 markdown, 9 code) ✓
- Walks projection, covariance, estimator, Monte Carlo recovery, scan, and
  figures ✓
- Mentions Section 11 and includes a synthetic-only disclaimer ✓

### 4. Reference outputs — PASS
All present and committed:
- `results/paper_v7/projection_check.csv` ✓
- `results/paper_v7/covariance_summary.csv` ✓
- `results/paper_v7/mc_recovery_6x6.csv` ✓
- `results/paper_v7/mc_recovery_117mode.csv` ✓
- `results/paper_v7/lambda_fpaired_scan.csv` ✓
- `results/paper_v7/reproduction_manifest.json` ✓
- `figures/paper_v7/covariance_blocks.png` ✓
- `figures/paper_v7/sn_scan_lambda_fpaired.png` ✓
- `figures/paper_v7/injected_recovered.png` ✓

### 5. README — PASS
- Has a "Reproducing Paper Results" section ✓
- Lists exact expected values (projection, 6x6, 117-mode, scan tables) ✓
- States synthetic-only scope clearly (disclaimer + limitations) ✓
- Does not overclaim (explicitly disclaims observational validation) ✓

### 6. Tests — PASS
- `python -m pytest -q` → 20 passed ✓
- `python scripts/run_prototype.py` → exit 0, outputs + manifest written ✓
- Manifest `validation_status` = `pass`, `validation_failures` = `[]` ✓

### 7. Citation / license — PASS
- `LICENSE` — MIT, Copyright (c) 2026 Corey Luisi ✓
- `CITATION.cff` — valid CFF 1.2.0, version `0.3.0` ✓

### 8. Real-data readiness remains separate — PASS
- No real data committed; `data/` holds only `.gitkeep`, `README.md`,
  `public_sources.yml` ✓
- No Planck maps / FITS / `.npy` / `.hdf5` artifacts tracked ✓
- CLASS/CAMB adapters are non-executing placeholders that raise a clear
  `ImportError` and state the base prototype does not run the solvers ✓
- No observational likelihood present ✓
- Tests perform no real network downloads (only `file://` URLs and `tmp_path`) ✓

## Expected paper values — all reproduce exactly

### Projection
```
||P_vis tau_1 P_vis||_F = 0
||P_vis I P_vis||_F     = 1
```

### 6x6
```
Tr(Delta C_6)    = 0
Tr(Delta C_6^2)  = 0.1828
F_A              = 0.0914
sigma_A          = 3.30771
```

### 117-mode
```
N_modes           = 117
Tr(Delta C_117)   = 0
Tr(Delta C_117^2) = 2
F_A               = 1
sigma_A           = 1
```

### Lambda scan (`q_SW = 0.44`)
| lambda_b | S/N, f_phi=1.0 | S/N, f_phi=0.5 | S/N, f_phi=0.15 |
| -------: | -------------: | -------------: | --------------: |
|     0.55 |         1.0933 |         0.5466 |          0.1640 |
|     0.65 |         0.9516 |         0.4758 |          0.1427 |
|     0.75 |         0.7763 |         0.3881 |          0.1164 |
|     0.85 |         0.5567 |         0.2783 |          0.0835 |
|     0.95 |         0.2615 |         0.1307 |          0.0392 |

All values match the README, the manifest expected values, and the paper's
Section 11 tables.

## Observations (non-blocking)

- Re-running `scripts/run_prototype.py` in this environment regenerated the
  committed CSV/PNG outputs with differences only at the **last 1–2 ULPs**
  (~1e-15 relative) of the full-precision float64 columns, plus minor PNG byte
  differences. These trace to newer numpy/BLAS and matplotlib versions, not to
  any change in the science: every documented/rounded value is identical and
  all validation tolerances pass. The committed reference outputs were left
  unchanged (restored after the verification run).

## Remaining optional polish

1. **Repository settings** (no GitHub MCP tool is available in this session to
   edit repo description/topics, so recording the recommendation here):
   - Description:
     `Synthetic low-ell CMB covariance prototype for visible-sector collapse / non-orientable topology proof-of-method checks.`
   - Topics: `cosmology`, `cmb`, `cosmic-topology`, `non-orientable-topology`,
     `python`, `reproducibility`, `synthetic-data`
2. (Optional) Pin numpy/matplotlib versions or round persisted CSV columns to a
   fixed precision if bit-identical committed outputs across library versions
   are desired. Not required for reproducibility — all validated values are
   stable to the documented precision.

## Conclusion

The stale gap analysis has been checked against the current `main` branch.
**Current `main` already satisfies the critical reproducibility requirements**
and is safe to link from the paper as a synthetic reproducibility companion.
The remaining items are optional polish only. No scientific results were
changed by this audit.
