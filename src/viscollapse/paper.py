"""Paper v7 Section 11 synthetic reproduction helpers.

This module defines the expected values for the synthetic paper-results
reproduction. It does not use real CMB data, Planck maps, CLASS/CAMB,
COMPACT eigenmodes, or a Planck likelihood.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import metadata
import json
from pathlib import Path
from typing import Any

import pandas as pd

from .constants import (
    ELL_MAX,
    ELL_MIN,
    FPAIRED_VALUES,
    LAMBDA_B_VALUES,
    N_MODES,
    Q_SW_DEFAULT,
    SEED_117,
    SEED_6X6,
)
from .covariance import template_117_mode, template_summary, toy_covariance_6x6
from .estimator import monte_carlo_recovery
from .projections import projection_check
from .scans import lambda_fpaired_scan, scan_column_name


PAPER_VERSION = "v7.1"
PAPER_SECTION = "Section 11"
DEFAULT_RESULTS_DIR = Path("results") / "paper_v7"
DEFAULT_FIGURES_DIR = Path("figures") / "paper_v7"

EXPECTED_PROJECTION = {
    "odd_projection_fro_norm": 0.0,
    "even_projection_fro_norm": 1.0,
}

EXPECTED_6X6 = {
    "trace": 0.0,
    "trace_square": 0.1828,
    "fisher": 0.0914,
    "sigma_A": 3.30771,
}

EXPECTED_117 = {
    "n_modes": 117,
    "trace": 0.0,
    "trace_square": 2.0,
    "fisher": 1.0,
    "sigma_A": 1.0,
}

EXPECTED_MC_6X6 = {
    0.0: {"Ahat_mean": 0.010639, "Ahat_SE": 0.007379},
    0.5: {"Ahat_mean": 0.495883, "Ahat_SE": 0.007484},
    1.0: {"Ahat_mean": 1.011686, "Ahat_SE": 0.007606},
}

EXPECTED_MC_117 = {
    0.0: {"Ahat_mean": -0.001235, "Ahat_SE": 0.004470},
    0.5: {"Ahat_mean": 0.496998, "Ahat_SE": 0.004485},
    1.0: {"Ahat_mean": 0.999660, "Ahat_SE": 0.004516},
}

EXPECTED_SCAN = {
    0.55: {1.0: 1.0933, 0.5: 0.5466, 0.15: 0.1640},
    0.65: {1.0: 0.9516, 0.5: 0.4758, 0.15: 0.1427},
    0.75: {1.0: 0.7763, 0.5: 0.3881, 0.15: 0.1164},
    0.85: {1.0: 0.5567, 0.5: 0.2783, 0.15: 0.0835},
    0.95: {1.0: 0.2615, 0.5: 0.1307, 0.15: 0.0392},
}


@dataclass(frozen=True)
class ReproductionBundle:
    """Container for synthetic paper-reproduction tables and diagnostics."""

    projection: dict[str, float]
    covariance_summary: pd.DataFrame
    mc6: pd.DataFrame
    mc117: pd.DataFrame
    scan: pd.DataFrame


def build_paper_reproduction() -> ReproductionBundle:
    """Build every synthetic table used in the paper v7 Section 11 prototype."""
    projection = projection_check()

    d6 = toy_covariance_6x6()
    summary6 = template_summary(d6)

    d117 = template_117_mode()
    summary117 = template_summary(d117)

    covariance_summary = pd.DataFrame(
        [
            {"template": "6x6 toy block", "n_modes": d6.shape[0], **summary6},
            {
                "template": "117-mode synthetic ring",
                "n_modes": d117.shape[0],
                **summary117,
            },
        ]
    )

    return ReproductionBundle(
        projection=projection,
        covariance_summary=covariance_summary,
        mc6=monte_carlo_recovery(d6, n_draws=200_000, seed=SEED_6X6),
        mc117=monte_carlo_recovery(d117, n_draws=50_000, seed=SEED_117),
        scan=lambda_fpaired_scan(),
    )


def validate_paper_reproduction(bundle: ReproductionBundle) -> list[str]:
    """Return validation failures against the paper v7 synthetic target values."""
    failures: list[str] = []

    for key, expected in EXPECTED_PROJECTION.items():
        _check_close(failures, f"projection.{key}", bundle.projection[key], expected)

    rows = {
        str(row.template): row._asdict()
        for row in bundle.covariance_summary.itertuples(index=False)
    }
    six = rows["6x6 toy block"]
    one17 = rows["117-mode synthetic ring"]
    for key, expected in EXPECTED_6X6.items():
        _check_close(failures, f"6x6.{key}", six[key], expected)
    for key, expected in EXPECTED_117.items():
        _check_close(failures, f"117.{key}", one17[key], expected)

    _validate_mc_table(failures, "mc6", bundle.mc6, EXPECTED_MC_6X6)
    _validate_mc_table(failures, "mc117", bundle.mc117, EXPECTED_MC_117)
    _validate_scan(failures, bundle.scan)
    return failures


def write_paper_outputs(
    bundle: ReproductionBundle,
    results_dir: str | Path = DEFAULT_RESULTS_DIR,
) -> dict[str, Path]:
    """Write synthetic paper-reproduction CSV and JSON manifest files."""
    output_dir = Path(results_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    projection_df = pd.DataFrame([bundle.projection])
    paths = {
        "projection_check": output_dir / "projection_check.csv",
        "covariance_summary": output_dir / "covariance_summary.csv",
        "mc_recovery_6x6": output_dir / "mc_recovery_6x6.csv",
        "mc_recovery_117mode": output_dir / "mc_recovery_117mode.csv",
        "lambda_fpaired_scan": output_dir / "lambda_fpaired_scan.csv",
        "reproduction_manifest": output_dir / "reproduction_manifest.json",
    }

    projection_df.to_csv(paths["projection_check"], index=False)
    bundle.covariance_summary.to_csv(paths["covariance_summary"], index=False)
    bundle.mc6.to_csv(paths["mc_recovery_6x6"], index=False)
    bundle.mc117.to_csv(paths["mc_recovery_117mode"], index=False)
    bundle.scan.to_csv(paths["lambda_fpaired_scan"], index=False)

    manifest = reproduction_manifest(bundle)
    paths["reproduction_manifest"].write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return paths


def reproduction_manifest(bundle: ReproductionBundle) -> dict[str, Any]:
    """Return a JSON-serializable manifest for the synthetic reproduction run."""
    failures = validate_paper_reproduction(bundle)
    return {
        "paper_version": PAPER_VERSION,
        "paper_section": PAPER_SECTION,
        "scope": "synthetic paper-results reproduction; not a real-data analysis",
        "package_version": _package_version(),
        "ell_range": {"ell_min": ELL_MIN, "ell_max": ELL_MAX, "n_modes": N_MODES},
        "seeds": {"seed_6x6": SEED_6X6, "seed_117": SEED_117},
        "monte_carlo_draws": {"six_by_six": 200_000, "one17_mode": 50_000},
        "scan_parameters": {
            "lambda_b_values": list(LAMBDA_B_VALUES),
            "fpaired_values": list(FPAIRED_VALUES),
            "q_sw": Q_SW_DEFAULT,
        },
        "expected_outputs": {
            "projection": EXPECTED_PROJECTION,
            "six_by_six": EXPECTED_6X6,
            "one17_mode": EXPECTED_117,
            "mc_recovery_6x6": EXPECTED_MC_6X6,
            "mc_recovery_117mode": EXPECTED_MC_117,
            "lambda_fpaired_scan": EXPECTED_SCAN,
        },
        "validation_status": "pass" if not failures else "fail",
        "validation_failures": failures,
    }


def _validate_mc_table(
    failures: list[str],
    label: str,
    table: pd.DataFrame,
    expected: dict[float, dict[str, float]],
) -> None:
    rows = {float(row.A_inj): row._asdict() for row in table.itertuples(index=False)}
    for amplitude, expected_row in expected.items():
        if amplitude not in rows:
            failures.append(f"{label}.{amplitude}: missing row")
            continue
        for key, expected_value in expected_row.items():
            _check_close(
                failures,
                f"{label}.{amplitude}.{key}",
                rows[amplitude][key],
                expected_value,
                abs_tol=5e-6,
            )


def _validate_scan(failures: list[str], scan: pd.DataFrame) -> None:
    rows = {float(row.lambda_b): row._asdict() for row in scan.itertuples(index=False)}
    for lambda_b, expected_curves in EXPECTED_SCAN.items():
        if lambda_b not in rows:
            failures.append(f"scan.{lambda_b}: missing row")
            continue
        row = rows[lambda_b]
        for fpaired, expected in expected_curves.items():
            column = scan_column_name(fpaired)
            _check_close(
                failures,
                f"scan.{lambda_b}.{column}",
                row[column],
                expected,
                abs_tol=5e-5,
            )


def _check_close(
    failures: list[str],
    label: str,
    actual: float,
    expected: float,
    *,
    abs_tol: float = 5e-5,
) -> None:
    if abs(float(actual) - float(expected)) > abs_tol:
        failures.append(f"{label}: expected {expected}, got {actual}")


def _package_version() -> str:
    try:
        return metadata.version("visible-sector-collapse-prototype")
    except metadata.PackageNotFoundError:
        return "editable-source"
