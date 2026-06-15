# visible-sector-collapse-prototype

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Tests](https://github.com/WowCorey/visible-sector-collapse-prototype/actions/workflows/tests.yml/badge.svg)](https://github.com/WowCorey/visible-sector-collapse-prototype/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Synthetic low-ell CMB covariance prototype for the discussion preprint:

**The Visible-Sector Collapse in Dressed Non-Orientable Cosmology: A Reidemeister-Schreier Obstruction to Thermal Anti-Homologous CMB Signatures, Gravitational Covariance, and Mirror Dark Matter**

Author: Corey Luisi.

Paper: discussion draft / preprint, arXiv link pending.

## Synthetic-only Disclaimer

> This repository generates synthetic toy covariance matrices only. It does not use real CMB data, Planck maps, CLASS/CAMB, COMPACT eigenmodes, masks, beams, foreground models, or a Planck likelihood. It is a proof-of-method validation of the mathematical machinery described in the associated discussion preprint.

This repository is a synthetic paper-results reproduction companion for the
prototype section of the paper. It is not a real-data analysis, does not run
external cosmology solvers, and does not claim observational validation.

## Reproducing Paper Results

From a fresh checkout:

```bash
python -m pip install -e ".[dev]"
python scripts/run_prototype.py
python -m pytest -q
```

The script reproduces the v7 Section 11 synthetic outputs, validates the
headline values, writes CSV/JSON files to `results/paper_v7/`, and writes PNG
figures to `figures/paper_v7/`. It exits with a nonzero status if a required
paper-value check fails.

The committed outputs are small synthetic reference outputs. They are included
so reviewers can compare a fresh run against the paper's Section 11 tables and
figures.

## Expected Output Files

```text
results/paper_v7/projection_check.csv
results/paper_v7/covariance_summary.csv
results/paper_v7/mc_recovery_6x6.csv
results/paper_v7/mc_recovery_117mode.csv
results/paper_v7/lambda_fpaired_scan.csv
results/paper_v7/reproduction_manifest.json
figures/paper_v7/covariance_blocks.png
figures/paper_v7/sn_scan_lambda_fpaired.png
figures/paper_v7/injected_recovered.png
```

## Expected Numerical Checks

Projection check:

```text
||P_vis tau_1 P_vis||_F = 0
||P_vis I P_vis||_F     = 1
```

6x6 toy block:

```text
Tr(Delta C_6)    = 0
Tr(Delta C_6^2)  = 0.1828
F_A              = 0.0914
sigma_A          = 3.30771
```

117-mode synthetic template:

```text
N_modes           = 117
Tr(Delta C_117)   = 0
Tr(Delta C_117^2) = 2
F_A               = 1
sigma_A           = 1
```

6x6 estimator recovery, using deterministic synthetic Gaussian Monte Carlo:

| A_inj | Ahat_mean | SE |
| ----: | --------: | -------: |
| 0.0 | 0.010639 | 0.007379 |
| 0.5 | 0.495883 | 0.007484 |
| 1.0 | 1.011686 | 0.007606 |

117-mode estimator recovery, using deterministic synthetic Gaussian Monte Carlo:

| A_inj | Ahat_mean | SE |
| ----: | --------: | -------: |
| 0.0 | -0.001235 | 0.004470 |
| 0.5 | 0.496998 | 0.004485 |
| 1.0 | 0.999660 | 0.004516 |

Analytic `lambda_b--f_phi_paired` scan using `q_SW = 0.44`:

| lambda_b | S/N, f_phi=1.0 | S/N, f_phi=0.5 | S/N, f_phi=0.15 |
| -------: | -------------: | -------------: | --------------: |
| 0.55 | 1.0933 | 0.5466 | 0.1640 |
| 0.65 | 0.9516 | 0.4758 | 0.1427 |
| 0.75 | 0.7763 | 0.3881 | 0.1164 |
| 0.85 | 0.5567 | 0.2783 | 0.0835 |
| 0.95 | 0.2615 | 0.1307 | 0.0392 |

## Master Notebook

The master notebook is:

```text
notebooks/reproduce_paper_results.ipynb
```

After installing the package, open and run the notebook from top to bottom. It
walks through the projection check, covariance summaries, quadratic estimator,
Monte Carlo recovery tables, analytic scan table, and generated figures. The
notebook is intentionally small and uses the same synthetic helpers as
`scripts/run_prototype.py`.

## Installation Details

Editable install:

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Conda:

```bash
conda env create -f environment.yml
conda activate visible-sector-collapse-prototype
python -m pip install -e ".[dev]"
```

Optional real-data readiness helpers:

```bash
python -m pip install -e ".[realdata]"
```

Optional CAMB import boundary:

```bash
python -m pip install -e ".[camb]"
```

CLASS/classy installation is environment-specific; follow current CLASS project
documentation before using the placeholder adapter.

## Prototype Components

- `viscollapse.paper`: builds, validates, and writes the v7 Section 11
  synthetic reproduction tables and manifest.
- `viscollapse.projections`: visible-sector projection checks.
- `viscollapse.covariance`: toy covariance templates and Fisher summaries.
- `viscollapse.estimator`: bias-subtracted quadratic estimator and synthetic
  Gaussian recovery draws.
- `viscollapse.scans`: analytic `lambda_b--f_phi_paired` scan.
- `viscollapse.figures`: synthetic PNG figure generation.
- `scripts/run_prototype.py`: one-command reproduction entry point.

See `docs/api_overview.md` for a concise API map.

## Real-data Readiness Caveat

The current implemented results are synthetic. Public Planck/LAMBDA products
and public solvers like CLASS/CAMB may be used in future lawful research
extensions only where source usage terms, versions, checksums, and citation
requirements are verified and recorded.

The presence of real-data interfaces in this repository does not mean the
paper's synthetic prototype has been compared with or supported by Planck data.

No real data files are committed. No Planck maps, FITS files, masks, beams,
noise models, foreground products, solver outputs, or large arrays should be
committed. No real Planck likelihood has been performed.

See:

- `docs/public_data_sources.md`
- `docs/real_data_readiness.md`
- `docs/citation_notes.md`

## Real-data smoke test

This repository includes an optional smoke-test command for explicitly selected
public CMB/FITS-style files. The smoke test verifies file access, checksum, and
metadata only. It does not perform a Planck likelihood, topology covariance fit,
or observational validation.

```bash
python -m pip install -e ".[realdata]"
python scripts/realdata_smoke_test.py --input data/raw/YOUR_PUBLIC_FILE.fits --source-name "manual public source"
```

See `docs/real_data_smoke_test.md` for details, URL usage, and optional FITS /
HEALPix inspection.

## Real-map low-ell extraction

An optional script can read a user-selected public HEALPix/FITS map and extract
low-ell `a_lm` coefficients:

```bash
python -m pip install -e ".[healpix]"
python scripts/extract_lowell_alms.py \
  --input data/raw/YOUR_PUBLIC_MAP.fits \
  --source-name "manual public source" \
  --lmax 10
```

This is not a Planck likelihood or model test. It only writes harmonic
coefficients, a simple `C_l` diagnostic, and a no-claims manifest. See
`docs/real_map_lowell_extraction.md`.

## Limitations

Included now:

- Reidemeister-Schreier visible-sector projection check
- visible odd thermal projection equals zero
- synthetic off-diagonal covariance templates
- 6x6 algebra sanity check
- 117-mode synthetic normalization check
- quadratic estimator recovery on toy Gaussian draws
- lambda_b--f_phi_paired analytic sensitivity scan
- small committed synthetic CSV/PNG reference outputs
- optional future real-data readiness scaffolding

Not included:

- public Planck maps
- masks, beams, anisotropic noise
- foreground residuals
- CLASS/CAMB execution
- COMPACT eigenmode implementation
- lensing/polarization likelihood
- Bayesian evidence versus LambdaCDM

## Project Structure

```text
visible-sector-collapse-prototype/
|-- README.md
|-- CITATION.cff
|-- LICENSE
|-- pyproject.toml
|-- requirements.txt
|-- environment.yml
|-- configs/paper_v7.yml
|-- src/viscollapse/
|-- scripts/run_prototype.py
|-- tests/
|-- notebooks/
|-- docs/
|-- data/
|-- results/paper_v7/
`-- figures/paper_v7/
```

## Citation

If you use this synthetic prototype, cite the associated discussion preprint
and this repository. See `CITATION.cff`.

## License

MIT License. See `LICENSE`.
