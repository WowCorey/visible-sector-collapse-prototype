# API Overview

This repository is a synthetic proof-of-method companion. Implemented numerical
results use toy covariance matrices only.

## Synthetic Paper Reproduction

- `viscollapse.paper`: builds, validates, and writes the v7 Section 11 synthetic
  reproduction tables and manifest.
- `viscollapse.projections`: visible-sector projection matrices and Frobenius
  norm checks.
- `viscollapse.covariance`: zero visible thermal block, 6x6 toy off-diagonal
  block, 117-mode synthetic template, and Fisher summaries.
- `viscollapse.estimator`: bias-subtracted quadratic estimator and deterministic
  synthetic Gaussian recovery tests.
- `viscollapse.scans`: analytic `lambda_b`--`f_phi_paired` toy sensitivity scan.
- `viscollapse.figures`: PNG generation for the synthetic covariance, scan, and
  injected-versus-recovered figures.
- `scripts/run_prototype.py`: one-command reproduction of the paper v7 Section
  11 synthetic outputs.

## Future Real-Data Readiness

- `viscollapse.data_sources`: loads the public-source manifest.
- `viscollapse.download`: explicit user-called download/cache helper with
  optional SHA-256 verification.
- `viscollapse.manifests`: checksum and YAML manifest helpers.
- `viscollapse.camb_adapter` and `viscollapse.class_adapter`: optional import
  boundaries only. They do not run CAMB or CLASS in the base package.

No real CMB data, Planck maps, CLASS/CAMB runs, COMPACT eigenmodes, or Planck
likelihood are included.
