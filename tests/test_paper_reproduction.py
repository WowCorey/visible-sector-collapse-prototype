import json

import pytest

from scripts.run_prototype import main
from viscollapse.paper import (
    EXPECTED_117,
    EXPECTED_6X6,
    build_paper_reproduction,
    validate_paper_reproduction,
)


def test_paper_reproduction_validation_passes():
    bundle = build_paper_reproduction()

    assert validate_paper_reproduction(bundle) == []
    covariance = {
        row.template: row._asdict()
        for row in bundle.covariance_summary.itertuples(index=False)
    }
    assert covariance["6x6 toy block"]["fisher"] == pytest.approx(EXPECTED_6X6["fisher"])
    assert covariance["117-mode synthetic ring"]["fisher"] == pytest.approx(EXPECTED_117["fisher"])


def test_run_prototype_writes_paper_outputs_and_manifest(tmp_path):
    results_dir = tmp_path / "results"
    figures_dir = tmp_path / "figures"

    exit_code = main(
        [
            "--output-dir",
            str(results_dir),
            "--figures-dir",
            str(figures_dir),
        ]
    )

    assert exit_code == 0
    for name in [
        "projection_check.csv",
        "covariance_summary.csv",
        "mc_recovery_6x6.csv",
        "mc_recovery_117mode.csv",
        "lambda_fpaired_scan.csv",
        "reproduction_manifest.json",
    ]:
        assert (results_dir / name).is_file()

    for name in [
        "covariance_blocks.png",
        "sn_scan_lambda_fpaired.png",
        "injected_recovered.png",
    ]:
        assert (figures_dir / name).is_file()

    manifest = json.loads((results_dir / "reproduction_manifest.json").read_text())
    assert manifest["package_version"] == "0.3.0"
    assert manifest["seeds"] == {"seed_117": 20260616, "seed_6x6": 20260615}
    assert manifest["validation_status"] == "pass"
    assert "expected_outputs" in manifest
    assert manifest["scope"].startswith("synthetic paper-results reproduction")
