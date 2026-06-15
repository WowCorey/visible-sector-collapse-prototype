# visible-sector-collapse-prototype

Synthetic low-(ell) covariance prototype for the discussion preprint:

**The Visible-Sector Collapse in Dressed Non-Orientable Cosmology: A Reidemeister-Schreier Obstruction to Thermal Anti-Homologous CMB Signatures, Gravitational Covariance, and Mirror Dark Matter**

Author: Corey Luisi.

## Synthetic-only disclaimer

> This repository generates synthetic toy covariance matrices only. It does not use real CMB data, Planck maps, CLASS/CAMB, COMPACT eigenmodes, masks, beams, foreground models, or a Planck likelihood. It is a proof-of-method validation of the mathematical machinery described in the associated discussion preprint.

This is not an observational cosmology analysis. It does not derive a Planck measurement, claim a detection, validate a cosmological model with data, or run an external Boltzmann solver. The code is a conservative proof-of-method implementation of the toy numerical checks used in the paper.

## What This Prototype Does

The package `viscollapse` reproduces a small set of synthetic sanity checks:

- visible-sector projection check;
- 6x6 toy off-diagonal covariance block;
- 117-mode synthetic low-(ell) normalization check for `2 <= ell <= 10`;
- bias-subtracted quadratic amplitude estimator;
- injected-amplitude recovery using deterministic synthetic Gaussian Monte Carlo draws;
- `lambda_b`--`f_phi_paired` analytic sensitivity scan;
- analytic Sachs-Wolfe ceiling recovery.

## Installation

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/WowCorey/visible-sector-collapse-prototype.git
cd visible-sector-collapse-prototype
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

On macOS or Linux:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Conda users can instead start from:

```bash
conda env create -f environment.yml
conda activate visible-sector-collapse-prototype
python -m pip install -e ".[dev]"
```

## Run the Prototype

```bash
python scripts/run_prototype.py
```

The script writes regenerated CSV files to `results/` and PNG figures to `figures/`. These generated outputs are ignored by git by default so the repository stays source-focused and reproducible.

Expected generated files include:

- `results/projection_check.csv`
- `results/toy_covariance_6x6.csv`
- `results/template_summaries.csv`
- `results/prototype_summary.csv`
- `results/mc_recovery_6x6.csv`
- `results/mc_recovery_117mode.csv`
- `results/lambda_fpaired_scan.csv`
- `figures/covariance_blocks.png`
- `figures/sn_scan_lambda_fpaired.png`
- `figures/injected_recovered.png`

## Run Tests

```bash
pytest
```

The tests verify the projection identities, covariance normalizations, deterministic estimator recovery, and analytic scan values. They do not compare against real data.

## Real-data readiness

The current implemented results are synthetic. Public Planck/LAMBDA data and
public solvers like CLASS/CAMB may be used in future lawful research extensions
where source usage terms, versions, checksums, and citation requirements are
verified and recorded.

This repository now includes:

- `data/public_sources.yml`, a cautious machine-readable public-source manifest;
- `docs/public_data_sources.md`, `docs/real_data_readiness.md`, and
  `docs/citation_notes.md`;
- optional public-data download/cache helpers with SHA-256 verification;
- optional CAMB and CLASS/classy adapter placeholders for future transfer work.

No real data files are committed. No Planck maps, FITS files, masks, beams,
noise models, foreground products, solver outputs, or large arrays should be
committed. No real Planck likelihood has been performed.

The presence of real-data interfaces in this repository does not mean the
paper's synthetic prototype has been validated against Planck data.

Optional readiness dependencies can be installed with:

```bash
python -m pip install -e ".[realdata]"
```

Optional CAMB support is separate:

```bash
python -m pip install -e ".[camb]"
```

CLASS/classy installation is environment-specific; follow the current CLASS
project documentation before using the placeholder adapter.

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

Analytic `lambda_b`--`f_phi_paired` scan using `q_SW = 0.44`:

| lambda_b | S/N, f_phi=1.0 | S/N, f_phi=0.5 | S/N, f_phi=0.15 |
| -------: | -------------: | -------------: | --------------: |
| 0.55 | 1.0933 | 0.5466 | 0.1640 |
| 0.65 | 0.9516 | 0.4758 | 0.1427 |
| 0.75 | 0.7763 | 0.3881 | 0.1164 |
| 0.85 | 0.5567 | 0.2783 | 0.0835 |
| 0.95 | 0.2615 | 0.1307 | 0.0392 |

This scan is an analytic toy sensitivity scan, not a data inference.

## Prototype Components

- `viscollapse.projections`: builds the visible-sector projector, sector-swap matrix, and Frobenius-norm projection checks.
- `viscollapse.covariance`: builds the zero visible thermal block, 6x6 toy off-diagonal block, 117-mode synthetic ring template, and trace/Fisher summaries.
- `viscollapse.estimator`: implements the bias-subtracted quadratic amplitude estimator for `C0 = I` and deterministic Gaussian recovery draws.
- `viscollapse.scans`: computes the analytic `lambda_b`--`f_phi_paired` sensitivity table.
- `viscollapse.figures`: generates the three review figures from synthetic outputs.
- `scripts/run_prototype.py`: runs the full reproducibility path and writes CSV/PNG artifacts.

## Limitations

Included:

- Reidemeister-Schreier visible-sector projection check
- visible odd thermal projection equals zero
- synthetic off-diagonal covariance templates
- 6x6 algebra sanity check
- 117-mode synthetic normalization check
- quadratic estimator recovery on toy Gaussian draws
- lambda_b--f_phi_paired analytic sensitivity scan

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
|-- LICENSE
|-- pyproject.toml
|-- requirements.txt
|-- environment.yml
|-- .gitignore
|-- .github/workflows/tests.yml
|-- src/viscollapse/
|-- scripts/run_prototype.py
|-- tests/
|-- notebooks/
|-- docs/
|-- data/
|-- results/.gitkeep
`-- figures/.gitkeep
```

## Citation Note

If you use this prototype in discussion, cite the associated discussion preprint by Corey Luisi and describe this repository as a synthetic toy covariance prototype or proof-of-method code. Do not cite it as observational analysis or a data-analysis pipeline.

## License

MIT License. See `LICENSE`.
