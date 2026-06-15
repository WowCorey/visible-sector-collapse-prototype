import numpy as np
import pytest

from viscollapse.projections import (
    projection_check,
    visible_even_projection,
    visible_odd_projection,
)

def test_odd_projection_is_zero():
    result = projection_check()
    assert result["odd_projection_fro_norm"] == pytest.approx(0.0)
    assert np.allclose(visible_odd_projection(), np.zeros((2, 2)))

def test_even_projection_is_one_and_nonzero():
    result = projection_check()
    assert result["even_projection_fro_norm"] == pytest.approx(1.0)
    assert np.linalg.norm(visible_even_projection(), ord="fro") > 0.0
