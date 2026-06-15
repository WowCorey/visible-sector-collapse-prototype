import numpy as np
import pytest

from viscollapse.constants import N_MODES
from viscollapse.covariance import (
    template_117_mode,
    template_summary,
    thermal_odd_block,
    toy_covariance_6x6,
)

def test_6x6_summary():
    d6 = toy_covariance_6x6()
    summary = template_summary(d6)
    assert d6.shape == (6, 6)
    assert np.allclose(d6, d6.T)
    assert np.allclose(np.diag(d6), 0.0)
    assert summary["trace"] == pytest.approx(0.0)
    assert summary["trace_square"] == pytest.approx(0.1828)
    assert summary["fisher"] == pytest.approx(0.0914)
    assert summary["sigma_A"] == pytest.approx(3.30771, rel=1e-5)

def test_117_mode_summary():
    d117 = template_117_mode()
    assert d117.shape == (N_MODES, N_MODES)
    assert np.allclose(d117, d117.T)
    assert np.allclose(np.diag(d117), 0.0)
    summary = template_summary(d117)
    assert summary["trace"] == pytest.approx(0.0)
    assert summary["trace_square"] == pytest.approx(2.0)
    assert summary["fisher"] == pytest.approx(1.0)
    assert summary["sigma_A"] == pytest.approx(1.0)

def test_thermal_odd_block_is_exactly_zero():
    block = thermal_odd_block(size=6)
    assert block.shape == (6, 6)
    assert np.count_nonzero(block) == 0
