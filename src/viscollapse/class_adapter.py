"""Optional CLASS/classy adapter placeholder for future transfer integration.

CLASS installation is environment-specific and is not part of the base install.
No CLASS execution is performed by this repository.
"""

from __future__ import annotations

import importlib
from types import ModuleType
from typing import Callable


def require_classy(
    importer: Callable[[str], ModuleType] = importlib.import_module,
) -> ModuleType:
    """Return the ``classy`` module, or raise a clear optional-dependency error."""
    try:
        return importer("classy")
    except ImportError as exc:
        raise ImportError(
            "CLASS/classy support is optional and installation is environment-specific. "
            "Follow the CLASS documentation before using this placeholder adapter. "
            "This repository does not run CLASS in the base synthetic prototype."
        ) from exc


def classy_available() -> bool:
    """Return whether ``classy`` can be imported in the current environment."""
    try:
        require_classy()
    except ImportError:
        return False
    return True
