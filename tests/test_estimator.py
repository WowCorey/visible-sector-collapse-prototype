import pytest

from viscollapse.constants import SEED_117, SEED_6X6
from viscollapse.covariance import template_117_mode, toy_covariance_6x6
from viscollapse.estimator import monte_carlo_recovery, quadratic_amplitude_estimator

def test_quadratic_estimator_rejects_zero_template():
    with pytest.raises(ValueError, match="zero norm"):
        quadratic_amplitude_estimator([[1.0, 2.0]], [[0.0, 0.0], [0.0, 0.0]])

def test_6x6_recovery_regression():
    df = monte_carlo_recovery(toy_covariance_6x6(), n_draws=200_000, seed=SEED_6X6)
    expected = {
        0.0: (0.010639, 0.007379),
        0.5: (0.495883, 0.007484),
        1.0: (1.011686, 0.007606),
    }
    for row in df.itertuples(index=False):
        mean, se = expected[row.A_inj]
        assert row.status == "pass"
        assert row.Ahat_mean == pytest.approx(mean, abs=2e-4)
        assert row.Ahat_SE == pytest.approx(se, abs=2e-4)

def test_117_mode_recovery_regression():
    df = monte_carlo_recovery(template_117_mode(), n_draws=50_000, seed=SEED_117)
    expected = {
        0.0: (-0.001235, 0.004470),
        0.5: (0.496998, 0.004485),
        1.0: (0.999660, 0.004516),
    }
    for row in df.itertuples(index=False):
        mean, se = expected[row.A_inj]
        assert row.status == "pass"
        assert row.Ahat_mean == pytest.approx(mean, abs=2e-4)
        assert row.Ahat_SE == pytest.approx(se, abs=2e-4)
