"""Optional CAMB adapter placeholder for future transfer integration.

CAMB is not required for the synthetic prototype or test suite. This adapter
only provides a clean optional import boundary for future real-data readiness.
"""

from __future__ import annotations

import importlib
from types import ModuleType
from typing import Callable


def require_camb(importer: Callable[[str], ModuleType] = importlib.import_module) -> ModuleType:
    """Return the CAMB module, or raise a helpful optional-dependency error."""
    try:
        return importer("camb")
    except ImportError as exc:
        raise ImportError(
            "CAMB support is optional. Install with `pip install .[camb]`. "
            "This repository does not run CAMB in the base synthetic prototype."
        ) from exc


def camb_available() -> bool:
    """Return whether CAMB can be imported in the current environment."""
    try:
        require_camb()
    except ImportError:
        return False
    return True
