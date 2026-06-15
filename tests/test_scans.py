import pytest

from viscollapse.scans import lambda_fpaired_scan

def test_scan_values():
    scan = lambda_fpaired_scan()
    expected = [
        (0.55, 1.0933, 0.5466, 0.1640),
        (0.65, 0.9516, 0.4758, 0.1427),
        (0.75, 0.7763, 0.3881, 0.1164),
        (0.85, 0.5567, 0.2783, 0.0835),
        (0.95, 0.2615, 0.1307, 0.0392),
    ]
    assert list(scan.columns) == [
        "lambda_b",
        "alpha_deg",
        "A_topo",
        "SW_ceiling_fpaired_1_fSW_1",
        "N_ring",
        "f_ring",
        "S_over_N_q044_fpaired_1_0",
        "S_over_N_q044_fpaired_0_5",
        "S_over_N_q044_fpaired_0_15",
    ]
    for row, (lambda_b, sn_1, sn_05, sn_015) in zip(scan.itertuples(index=False), expected):
        assert row.lambda_b == pytest.approx(lambda_b)
        assert row.S_over_N_q044_fpaired_1_0 == pytest.approx(sn_1, abs=5e-5)
        assert row.S_over_N_q044_fpaired_0_5 == pytest.approx(sn_05, abs=5e-5)
        assert row.S_over_N_q044_fpaired_0_15 == pytest.approx(sn_015, abs=5e-5)
