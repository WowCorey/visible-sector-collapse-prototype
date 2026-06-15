# Data Directory

This directory is reserved for explicit, user-managed real-data readiness work.

No real CMB data, Planck maps, FITS files, solver outputs, masks, beams, noise
models, foreground products, NumPy arrays, or large external files are committed
to this repository.

The intended local layout is:

```text
data/
├── public_sources.yml
├── raw/       # ignored: manually selected public products
├── cache/     # ignored: optional downloader cache
└── external/  # ignored: external solver or archive outputs
```

Users are responsible for verifying current data/source usage terms and
publication citation requirements before downloading or publishing results
based on any public resource.
