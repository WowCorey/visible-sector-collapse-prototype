# Real-Data Readiness

The current implemented results in this repository are synthetic proof-of-method
checks. The real-data readiness layer prepares optional interfaces for future
lawful public-data work, but it is not yet a likelihood analysis.

The presence of real-data interfaces in this repository does not mean the
paper's synthetic prototype has been validated against Planck data.

## Current Scope

Included now:

- synthetic covariance prototype;
- public-data source manifest;
- optional public-data download scaffold;
- SHA-256 checksum support for downloaded files;
- optional interfaces for future Planck/LAMBDA products;
- optional placeholders for future CLASS/CAMB transfer integration;
- documentation explaining public-source and citation responsibilities.

Not included yet:

- full Planck likelihood analysis;
- full-sky mask/beam/noise/foreground treatment;
- physical COMPACT eigenmode implementation;
- non-orientable spin-2 covariance implementation;
- Bayesian evidence versus LambdaCDM;
- detection claim;
- observational inference.

## Future Pipeline Stages

Future real-data work should proceed only after the required data terms,
software licenses, and citations are verified. A conservative future path would
be:

1. Select lawful public data products.
2. Record citation requirements, source URLs, release versions, and terms.
3. Download through an explicit user-called script or command.
4. Verify SHA-256 checksums and record them in a reproducibility manifest.
5. Keep raw data, caches, FITS files, solver outputs, and large arrays out of git.
6. Build masks, noise models, beam functions, and foreground-residual handling.
7. Build the LambdaCDM baseline covariance.
8. Build the topology covariance.
9. Validate null cases and synthetic recovery cases.
10. Only then evaluate a likelihood comparison.

## Optional Local Cache

The helper `viscollapse.download.download_file` can write to `data/cache/` or a
user-provided destination. It performs no automatic downloads and is not called
by tests. Users should provide expected SHA-256 checksums whenever possible.

Example pattern:

```python
from viscollapse.download import download_file

download_file(
    url="https://example.org/public-product.fits",
    dest="data/cache/public-product.fits",
    expected_sha256="replace-with-verified-sha256",
)
```

Do not use the placeholder URL above for research. Select a real public product
only after verifying source terms, release version, and citation requirements.

## Optional Solver Interfaces

CAMB and CLASS are not required for installation, tests, or the synthetic
prototype. The adapter modules provide only import boundaries for future work:

- `viscollapse.camb_adapter.require_camb()` raises a helpful message unless
  CAMB is installed with an optional environment such as `pip install .[camb]`.
- `viscollapse.class_adapter.require_classy()` documents that CLASS/classy
  installation is environment-specific and must follow CLASS project guidance.

No CLASS/CAMB topology calculation is performed in this repository.
