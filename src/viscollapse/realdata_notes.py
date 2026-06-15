"""Scope notes for the real-data readiness scaffold.

The synthetic prototype is implemented now. The real-data interfaces in this
package are preparation for future lawful public-data work only.
"""

from __future__ import annotations


REALDATA_SCOPE_NOTE = (
    "The presence of real-data interfaces in this repository does not mean the "
    "paper's synthetic prototype has been compared with or supported by Planck data."
)

INCLUDED_NOW = (
    "synthetic covariance prototype",
    "public-data source manifest",
    "optional public-data download scaffold",
    "SHA-256 checksum helpers",
    "optional future Planck/LAMBDA interface notes",
    "optional future CLASS/CAMB adapter placeholders",
)

NOT_INCLUDED_YET = (
    "full Planck likelihood analysis",
    "full-sky mask/beam/noise/foreground treatment",
    "physical COMPACT eigenmode implementation",
    "non-orientable spin-2 covariance implementation",
    "Bayesian evidence versus LambdaCDM",
    "observational claim",
    "observational inference",
)


def readiness_scope() -> dict[str, tuple[str, ...] | str]:
    """Return the included/not-included real-data readiness scope."""
    return {
        "scope_note": REALDATA_SCOPE_NOTE,
        "included_now": INCLUDED_NOW,
        "not_included_yet": NOT_INCLUDED_YET,
    }
