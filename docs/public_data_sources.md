# Public Data Sources

This page records candidate public resources for future real-data readiness.
It is a source/citation planning document, not evidence that a real-data
analysis has been performed.

| Source | Type | Intended future use | Status | Citation note |
| --- | --- | --- | --- | --- |
| Planck Legacy Archive | public CMB data products | future maps/products | public source, terms to verify | cite Planck Collaboration |
| NASA LAMBDA | public CMB archive | future Planck/LAMBDA products | public source, terms to verify | cite LAMBDA / product papers |
| CLASS | public Boltzmann code | future transfer functions | public code, citation required | cite CLASS papers |
| CAMB | public Boltzmann code | future transfer functions | public code, citation required | cite CAMB papers/docs |
| COMPACT-related work | methodological context | future eigenmode/covariance methods | to verify | do not claim implementation |

The machine-readable companion file is `data/public_sources.yml`.

## Source Notes

- Planck Legacy Archive: ESA Planck public products are available through
  `https://pla.esac.esa.int/`. Future work must record exact product names,
  release versions, checksums, citations, and current usage terms.
- NASA LAMBDA: Planck-related public products and documentation are available
  through `https://lambda.gsfc.nasa.gov/product/planck/`. Future work must
  record whether a file came from LAMBDA, ESA, IRSA, or another public mirror.
- Planck 2018 papers and likelihood references: future likelihood work must
  cite the relevant Planck Collaboration papers and documentation. This
  repository does not currently run a Planck likelihood.
- CLASS: the public CLASS project is documented at `https://class-code.net/`
  with code at `https://github.com/lesgourg/class_public`. Future transfer
  integration must follow the current CLASS installation and citation guidance.
- CAMB: CAMB is documented at `https://camb.info/` and
  `https://camb.readthedocs.io/`, with code at `https://github.com/cmbant/CAMB`.
  Future transfer integration must follow the current CAMB installation and
  citation guidance.
- COMPACT-related work: no physical COMPACT eigenmode implementation is
  included. Any future method or code must be verified and cited before use.

No downloaded FITS files, maps, masks, solver outputs, or large arrays should
be committed to this repository.
