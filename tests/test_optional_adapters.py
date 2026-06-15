import pytest

from viscollapse.camb_adapter import require_camb
from viscollapse.class_adapter import require_classy


def _missing_importer(name):
    raise ModuleNotFoundError(name)


def test_missing_optional_camb_has_clean_error_message():
    with pytest.raises(ImportError, match=r"CAMB support is optional.*\.\[camb\]"):
        require_camb(importer=_missing_importer)


def test_missing_optional_classy_has_clean_error_message():
    with pytest.raises(ImportError, match="CLASS/classy support is optional"):
        require_classy(importer=_missing_importer)
