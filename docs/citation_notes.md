# Citation Notes

Future publications or public results based on real public data or external
solvers must verify and follow the current citation instructions for every
source used.

This repository currently implements synthetic proof-of-method checks only. It
does not use Planck maps, run a Planck likelihood, execute CLASS/CAMB, or
implement physical COMPACT eigenmodes.

## Future Citation Responsibilities

- Planck products: cite the relevant Planck Collaboration papers for each
  selected data release, map, likelihood product, mask, or ancillary file.
- NASA LAMBDA: cite NASA LAMBDA if LAMBDA-hosted products or documentation are
  used, and cite the underlying product papers.
- CLASS: cite the CLASS papers requested by the CLASS project if CLASS is used
  for future transfer functions or related calculations.
- CAMB: cite the CAMB papers/docs requested by the CAMB project if CAMB is used
  for future transfer functions or related calculations.
- COMPACT/eigenmode methods: cite only verified future sources and do not claim
  implementation until a physical implementation exists and is documented.

## Reproducibility Records

Future real-data work should record:

- source URL;
- access date;
- product version or release name;
- local cache path;
- SHA-256 checksum;
- citation text or DOI/arXiv reference;
- terms or license note verified at the time of use.

The file `data/public_sources.yml` is a starting manifest, not a substitute for
product-specific citation and terms review.
